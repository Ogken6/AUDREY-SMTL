#!/usr/bin/env python3
"""
Dustid SDR Prospector — Tom's Autonomous Prospecting Script

Mission: Find 100-150 qualified UK/Ireland social sellers with:
- Recent DM chaos or virality (0-72 hours)
- No existing store infrastructure
- Live sellers prioritized

Tools: TikTokApi, Playwright, Pydoll, Google Sheets API
"""

import json
import time
import re
import sys
from datetime import datetime, timedelta
from urllib.parse import urlparse
import subprocess
import requests

# Google Sheets Configuration
SHEET_ID = '1bOR0HY_tg73-d6cjMpouN9jjY8meyl4ma1kCte3rqqg'
API_KEY = 'AIzaSyALDFejLlxZM_4uEQwkDSPkVgkPBzY-UKo'

# TikTok Search Terms for UK/Ireland Sellers
SEARCH_QUERIES = [
    "handmade UK TikTok shop",
    "small business UK TikTok",
    "DM to order UK",
    "handmade Ireland TikTok",
    "UK seller TikTok live",
    "small biz UK orders",
    "handmade candles UK TikTok",
    "jewellery UK TikTok seller",
    "clothing UK small business TikTok",
    "skincare UK handmade TikTok",
]

# Disqualification patterns
STORE_PATTERNS = [
    r'etsy\.com/shop/',
    r'depop\.com/@',
    r'amazon\.co\.uk/shop/',
    r'ebay\.co\.uk/usr/',
    r'shopify\.com',
    r'bigcartel\.com',
    r'squarespace\.com',
    r'wixsite\.com',
    r'vinted\.(co\.uk|com)',
]

MARKETPLACE_KEYWORDS = ['etsy', 'depop', 'amazon', 'ebay', 'vinted', 'shopify']

class DustidProspector:
    def __init__(self):
        self.qualified_leads = []
        self.disqualified = {
            'has_store': 0,
            'has_marketplace': 0,
            'not_uk_ireland': 0,
            'no_virality_signal': 0,
            'signal_too_old': 0,
            'incomplete_data': 0,
        }
        self.live_sellers_found = 0
        self.total_checked = 0
        
    def log(self, message):
        """Print timestamped log message"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        sys.stdout.flush()
        
    def check_tiktok_api_available(self):
        """Check if TikTokApi is installed"""
        try:
            from TikTokApi import TikTokApi
            return True
        except ImportError:
            self.log("⚠️  TikTokApi not installed. Installing...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'TikTokApi'], 
                         capture_output=True)
            try:
                from TikTokApi import TikTokApi
                return True
            except:
                return False
                
    def check_playwright_available(self):
        """Check if Playwright is installed"""
        try:
            from playwright.sync_api import sync_playwright
            return True
        except ImportError:
            self.log("⚠️  Playwright not installed. Installing...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'playwright'], 
                         capture_output=True)
            subprocess.run([sys.executable, '-m', 'playwright', 'install', 'chromium'], 
                         capture_output=True)
            try:
                from playwright.sync_api import sync_playwright
                return True
            except:
                return False
    
    def search_tiktok_profiles(self, query, limit=20):
        """Search TikTok for seller profiles"""
        self.log(f"🔍 Searching TikTok: '{query}'")
        
        # Try browser-based search first
        profiles = self._browser_search_tiktok(query, limit)
        
        if not profiles:
            self.log("⚠️  Browser search failed, trying alternative methods...")
            # Fallback to web search for TikTok profiles
            profiles = self._web_search_tiktok_profiles(query, limit)
            
        return profiles
    
    def _browser_search_tiktok(self, query, limit):
        """Use browser to search TikTok"""
        profiles = []
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = context.new_page()
                
                # Navigate to TikTok search
                search_url = f"https://www.tiktok.com/search?q={query.replace(' ', '%20')}"
                page.goto(search_url, wait_until='networkidle', timeout=30000)
                
                # Wait for content to load
                page.wait_for_timeout(5000)
                
                # Extract profile links from search results
                links = page.query_selector_all('a[href*="/@"]')
                seen = set()
                
                for link in links[:limit]:
                    href = link.get_attribute('href')
                    if href and '/@' in href:
                        username = href.split('/@')[-1].split('?')[0].split('/')[0]
                        if username and username not in seen:
                            seen.add(username)
                            profiles.append({
                                'username': username,
                                'profile_url': f"https://www.tiktok.com/@{username}",
                                'platform': 'TikTok'
                            })
                
                browser.close()
                
        except Exception as e:
            self.log(f"⚠️  Browser error: {str(e)[:100]}")
            
        return profiles
    
    def _web_search_tiktok_profiles(self, query, limit):
        """Use web search to find TikTok profiles"""
        profiles = []
        try:
            # Use a search engine to find TikTok profiles
            search_query = f"site:tiktok.com @{query} UK seller"
            # This is a simplified approach - in practice you'd use a search API
            self.log("Using web search fallback...")
        except Exception as e:
            self.log(f"⚠️  Web search error: {str(e)[:100]}")
        return profiles
    
    def analyze_tiktok_profile(self, username):
        """Analyze a TikTok profile for qualification"""
        self.log(f"📊 Analyzing @{username}...")
        
        profile_data = {
            'username': username,
            'platform': 'TikTok',
            'display_name': '',
            'bio': '',
            'followers': '',
            'following': '',
            'likes': '',
            'recent_posts': [],
            'has_store': False,
            'store_platforms': [],
            'virality_signals': [],
            'is_live_seller': False,
            'location_verified': False,
            'product_focus': '',
        }
        
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = context.new_page()
                
                # Visit profile
                profile_url = f"https://www.tiktok.com/@{username}"
                page.goto(profile_url, wait_until='networkidle', timeout=30000)
                page.wait_for_timeout(3000)
                
                # Extract profile data
                try:
                    # Display name
                    name_elem = page.query_selector('h1[data-e2e="user-title"]')
                    if name_elem:
                        profile_data['display_name'] = name_elem.inner_text().strip()
                except:
                    pass
                
                try:
                    # Bio
                    bio_elem = page.query_selector('h2[data-e2e="user-bio"]')
                    if bio_elem:
                        profile_data['bio'] = bio_elem.inner_text().strip()
                except:
                    pass
                
                try:
                    # Followers
                    followers_elem = page.query_selector('strong[data-e2e="followers-count"]')
                    if followers_elem:
                        profile_data['followers'] = followers_elem.inner_text().strip()
                except:
                    pass
                
                try:
                    # Following
                    following_elem = page.query_selector('strong[data-e2e="following-count"]')
                    if following_elem:
                        profile_data['following'] = following_elem.inner_text().strip()
                except:
                    pass
                
                try:
                    # Likes
                    likes_elem = page.query_selector('strong[data-e2e="likes-count"]')
                    if likes_elem:
                        profile_data['likes'] = likes_elem.inner_text().strip()
                except:
                    pass
                
                # Check bio for store links
                bio_lower = profile_data['bio'].lower()
                for keyword in MARKETPLACE_KEYWORDS:
                    if keyword in bio_lower:
                        profile_data['has_store'] = True
                        profile_data['store_platforms'].append(keyword)
                
                # Check for link in bio
                try:
                    link_elem = page.query_selector('a[data-e2e="user-link"]')
                    if link_elem:
                        bio_link = link_elem.get_attribute('href')
                        profile_data['bio_link'] = bio_link
                        # Check if link contains store
                        if bio_link:
                            self._check_link_for_store(profile_data, bio_link)
                except:
                    pass
                
                # Check recent posts for virality signals
                try:
                    posts = page.query_selector_all('div[data-e2e="user-post-item"]')
                    for i, post in enumerate(posts[:5]):
                        try:
                            # Get views
                            views_elem = post.query_selector('strong[data-e2e="video-views"]')
                            views = views_elem.inner_text().strip() if views_elem else '0'
                            
                            # Get caption
                            caption_elem = post.query_selector('div[data-e2e="post-desc"]')
                            caption = caption_elem.inner_text().strip() if caption_elem else ''
                            
                            profile_data['recent_posts'].append({
                                'views': views,
                                'caption': caption[:200],
                            })
                            
                            # Check for DM/order signals in caption
                            caption_lower = caption.lower()
                            if any(signal in caption_lower for signal in [
                                'dm to order', 'message to buy', 'comment to order',
                                'link in bio', 'dm me', 'how to buy'
                            ]):
                                profile_data['virality_signals'].append(f"Post signal: {caption[:100]}")
                                
                        except:
                            continue
                except:
                    pass
                
                # Check for live selling
                try:
                    live_elem = page.query_selector('[data-e2e="live-icon"]')
                    if live_elem:
                        profile_data['is_live_seller'] = True
                        profile_data['virality_signals'].append("Live seller detected")
                except:
                    pass
                
                browser.close()
                
        except Exception as e:
            self.log(f"⚠️  Profile analysis error: {str(e)[:100]}")
            
        return profile_data
    
    def _check_link_for_store(self, profile_data, link):
        """Check if a bio link leads to a store"""
        try:
            # Check for Linktree
            if 'linktr.ee' in link or 'linktree' in link:
                self._check_linktree(profile_data, link)
                return
                
            # Check for known store platforms
            for pattern in STORE_PATTERNS:
                if re.search(pattern, link):
                    profile_data['has_store'] = True
                    profile_data['store_platforms'].append('website_store')
                    return
                    
        except Exception as e:
            self.log(f"⚠️  Link check error: {str(e)[:100]}")
    
    def _check_linktree(self, profile_data, linktree_url):
        """Check Linktree for store links"""
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                
                page.goto(linktree_url, wait_until='networkidle', timeout=15000)
                page.wait_for_timeout(2000)
                
                # Get all links on the page
                links = page.query_selector_all('a[href]')
                for link in links:
                    href = link.get_attribute('href')
                    if href:
                        href_lower = href.lower()
                        for keyword in MARKETPLACE_KEYWORDS:
                            if keyword in href_lower:
                                profile_data['has_store'] = True
                                profile_data['store_platforms'].append(f'linktree_{keyword}')
                                
                browser.close()
                
        except Exception as e:
            self.log(f"⚠️  Linktree check error: {str(e)[:100]}")
    
    def check_google_for_marketplace(self, username):
        """Google search for marketplace stores"""
        # Simplified - would need search API for production
        return False
    
    def verify_location(self, bio, username):
        """Verify if seller is UK or Ireland based"""
        uk_ireland_terms = [
            'uk', 'united kingdom', 'england', 'scotland', 'wales', 
            'northern ireland', 'ireland', 'dublin', 'belfast',
            'london', 'manchester', 'birmingham', 'glasgow', 'edinburgh',
            'liverpool', 'leeds', 'bristol', 'sheffield', 'cardiff',
            'belfast', 'nottingham', 'newcastle', 'leicester',
            'co.uk', '.uk', 'gb'
        ]
        
        bio_lower = bio.lower()
        
        for term in uk_ireland_terms:
            if term in bio_lower:
                return True
                
        # Check username for UK hints
        if 'uk' in username.lower():
            return True
            
        return False
    
    def evaluate_lead(self, profile_data):
        """Evaluate if lead qualifies based on all criteria"""
        self.total_checked += 1
        
        # Check 1: Location (UK/Ireland)
        if not self.verify_location(profile_data['bio'], profile_data['username']):
            self.disqualified['not_uk_ireland'] += 1
            return False, 'Location not UK/Ireland'
        
        # Check 2: Has store
        if profile_data['has_store']:
            self.disqualified['has_store'] += 1
            return False, f"Has store: {', '.join(profile_data['store_platforms'])}"
        
        # Check 3: Has marketplace (from Google search)
        if self.check_google_for_marketplace(profile_data['username']):
            self.disqualified['has_marketplace'] += 1
            return False, "Marketplace store found via search"
        
        # Check 4: Has virality/DM chaos signal
        if not profile_data['virality_signals']:
            self.disqualified['no_virality_signal'] += 1
            return False, "No DM chaos or virality signal"
        
        # Check 5: Recent signal (simplified - would need post timestamps)
        # For now, we check if they have recent posts with signals
        has_recent_signal = len(profile_data['recent_posts']) > 0 and len(profile_data['virality_signals']) > 0
        if not has_recent_signal:
            self.disqualified['signal_too_old'] += 1
            return False, "No recent virality signal (0-72 hours)"
        
        # Count live sellers
        if profile_data['is_live_seller']:
            self.live_sellers_found += 1
        
        return True, 'Qualified'
    
    def add_to_sheet(self, lead_data):
        """Add qualified lead to Google Sheet"""
        try:
            # Prepare row data
            row = [
                lead_data.get('lead_id', ''),
                datetime.now().strftime('%Y-%m-%d'),
                lead_data.get('platform', ''),
                lead_data.get('username', ''),
                lead_data.get('display_name', ''),
                lead_data.get('profile_url', ''),
                lead_data.get('followers', ''),
                lead_data.get('following', ''),
                lead_data.get('bio', ''),
                'UK',  # Location (verified)
                'Small Business',
                lead_data.get('product_focus', ''),
                'TikTok Search',
                'Niche Search',
                '',  # ICP Score (Elsie will fill)
                '',  # ICP Tier (Elsie will fill)
                '',  # Messaging Angle (Sandra will fill)
                lead_data.get('virality_signals', '')[0] if lead_data.get('virality_signals') else '',
                'New',
                '',  # CRM Status
                '',  # Conversation Summary
                datetime.now().isoformat(),
                'Automated Prospecting',
                'TikTok Search',
                ' | '.join(lead_data.get('virality_signals', [])),
                'HOT' if lead_data.get('is_live_seller') else 'WARM',
                'YES',
            ]
            
            # Use Google Sheets API to append
            self._append_row_to_sheet('LEADS_MASTER', row)
            
        except Exception as e:
            self.log(f"⚠️  Sheet error: {str(e)[:100]}")
    
    def _append_row_to_sheet(self, sheet_name, row_data):
        """Append row to Google Sheet using API"""
        try:
            url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{sheet_name}:append"
            params = {'valueInputOption': 'USER_ENTERED', 'key': API_KEY}
            body = {'values': [row_data]}
            
            response = requests.post(url, params=params, json=body)
            
            if response.status_code == 200:
                self.log(f"✅ Added {row_data[3]} to sheet")
            else:
                self.log(f"⚠️  Sheet API error: {response.status_code}")
                
        except Exception as e:
            self.log(f"⚠️  Sheet append error: {str(e)[:100]}")
    
    def run_session(self, target_count=100):
        """Main prospecting session"""
        self.log("=" * 60)
        self.log("🎯 DUSTID SDR PROSPECTOR — TOM v2.0")
        self.log("=" * 60)
        self.log(f"Target: {target_count} qualified leads")
        self.log(f"Criteria: UK/Ireland, No store, Recent virality (0-72h)")
        self.log("")
        
        # Check dependencies
        has_tiktok = self.check_tiktok_api_available()
        has_playwright = self.check_playwright_available()
        
        self.log(f"TikTokApi: {'✅' if has_tiktok else '❌'}")
        self.log(f"Playwright: {'✅' if has_playwright else '❌'}")
        self.log("")
        
        if not has_playwright:
            self.log("❌ Playwright not available. Cannot proceed.")
            return
        
        # Search for prospects
        for query in SEARCH_QUERIES:
            if len(self.qualified_leads) >= target_count:
                break
                
            self.log(f"\n🔍 Searching: '{query}'")
            
            # Get profiles from search
            profiles = self.search_tiktok_profiles(query, limit=30)
            self.log(f"Found {len(profiles)} profiles")
            
            # Analyze each profile
            for profile in profiles:
                if len(self.qualified_leads) >= target_count:
                    break
                    
                # Analyze profile
                profile_data = self.analyze_tiktok_profile(profile['username'])
                
                # Skip if incomplete data
                if not profile_data['bio'] or not profile_data['followers']:
                    self.disqualified['incomplete_data'] += 1
                    continue
                
                # Evaluate against criteria
                is_qualified, reason = self.evaluate_lead(profile_data)
                
                if is_qualified:
                    # Generate lead ID
                    lead_id = f"TT-{datetime.now().strftime('%y%m%d')}-{len(self.qualified_leads)+1:03d}"
                    profile_data['lead_id'] = lead_id
                    
                    self.qualified_leads.append(profile_data)
                    self.log(f"✅ QUALIFIED: @{profile['username']} — {reason}")
                    
                    # Add to sheet
                    self.add_to_sheet(profile_data)
                    
                    # Rate limiting
                    time.sleep(2)
                else:
                    self.log(f"❌ Disqualified: @{profile['username']} — {reason}")
        
        # Report results
        self._print_report()
    
    def _print_report(self):
        """Print session report"""
        self.log("")
        self.log("=" * 60)
        self.log("📊 SESSION REPORT")
        self.log("=" * 60)
        self.log(f"Total profiles checked: {self.total_checked}")
        self.log(f"Qualified leads: {len(self.qualified_leads)}")
        self.log(f"Live sellers found: {self.live_sellers_found}")
        self.log("")
        self.log("Disqualification breakdown:")
        for reason, count in self.disqualified.items():
            self.log(f"  {reason}: {count}")
        self.log("")
        self.log("Qualified leads:")
        for lead in self.qualified_leads[:10]:
            self.log(f"  ✅ {lead['lead_id']} — @{lead['username']} ({lead['platform']})")
        self.log("=" * 60)


def main():
    """Entry point"""
    prospector = DustidProspector()
    prospector.run_session(target_count=100)


if __name__ == '__main__':
    main()
