"""
Product Search Agent - Finds products based on specifications.
"""
from typing import Dict, Any, Optional, List
from agents.base_agent import BaseAgent
from agents.web_navigator import WebNavigatorAgent
from config import Config
from bs4 import BeautifulSoup
import re
import asyncio
import json

class ProductSearchAgent(BaseAgent):
    """Agent responsible for searching and finding products on websites."""
    
    def __init__(self, openai_client, web_navigator: WebNavigatorAgent):
        super().__init__("ProductSearch", openai_client)
        self.web_navigator = web_navigator
    
    async def extract_product_specs(self, user_query: str) -> Dict[str, Any]:
        """Extract product specifications from user query using OpenAI."""
        try:
            prompt = f"""
            Extract product specifications from the following user query. Return a JSON object with:
            - product_name: The main product name
            - brand: The brand name (if mentioned)
            - specifications: A dictionary of key-value pairs (e.g., {{"storage": "256GB", "color": "white", "model": "15 Pro"}})
            - website: The website URL if mentioned, otherwise return null
            
            User Query: {user_query}
            
            Return only valid JSON, no additional text.
            """
            
            response = await self.openai_client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts product information from user queries. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                timeout=30.0
            )
            
            result = json.loads(response.choices[0].message.content)
            self.log(f"Extracted product specs: {result}")
            return result
        
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                self.log("API quota exceeded, using fallback parser", "warning")
            else:
                self.log(f"Error extracting product specs: {error_msg}, using fallback parser", "warning")
            return self._simple_parse_query(user_query)
    
    def _simple_parse_query(self, query: str) -> Dict[str, Any]:
        """Simple fallback parser for product specifications."""
        specs = {}
        if not query:
            query = ""
        query_lower = query.lower()
        
        # Extract storage
        storage_match = re.search(r'(\d+)\s*(gb|tb)', query_lower)
        if storage_match:
            specs["storage"] = storage_match.group(0).upper()
        
        # Extract color
        colors = ["white", "black", "blue", "red", "green", "yellow", "purple", "pink", "gray", "silver", "gold"]
        for color in colors:
            if color in query_lower:
                specs["color"] = color
                break
        
        # Extract model numbers
        model_match = re.search(r'(\d+)\s*(pro|max|plus|mini)', query_lower)
        if model_match:
            specs["model"] = model_match.group(0)
        
        # Extract brand
        brands = ["apple", "samsung", "google", "sony", "lg", "nike", "adidas"]
        for brand in brands:
            if brand in query_lower:
                return {
                    "product_name": query,
                    "brand": brand.capitalize(),
                    "specifications": specs,
                    "website": None
                }
        
        return {
            "product_name": query,
            "brand": None,
            "specifications": specs,
            "website": None
        }
    
    async def determine_website(self, product_specs: Dict[str, Any]) -> str:
        """Determine the website URL based on product specifications."""
        brand = (product_specs.get("brand") or "").lower()
        product_name = (product_specs.get("product_name") or "").lower()
        
        # Map brands to their websites
        website_map = {
            "apple": "https://www.apple.com",
            "samsung": "https://www.samsung.com",
            "google": "https://store.google.com",
            "sony": "https://www.sony.com",
            "lg": "https://www.lg.com",
            "nike": "https://www.nike.com",
            "adidas": "https://www.adidas.com"
        }
        
        # Check if website is already specified
        if product_specs.get("website"):
            return product_specs["website"]
        
        # Check brand mapping
        for brand_key, website in website_map.items():
            if brand_key in brand or brand_key in product_name:
                return website
        
        # Default: try to infer from product name
        if "iphone" in product_name or "ipad" in product_name or "mac" in product_name or "apple" in product_name:
            return "https://www.apple.com"
        
        return None
    
    async def find_search_box_universal(self, page) -> Optional[Dict[str, Any]]:
        """Universal method to find search box on any website using multiple strategies."""
        try:
            current_url = page.url
            
            # Special handling for Apple.com - need to click search icon first
            if "apple.com" in current_url.lower():
                self.log("🍎 Detected Apple.com - opening search menu first...")
                apple_search_icons = [
                    "#ac-gn-searchform",
                    "button.ac-gn-searchform-submit",
                    "a[aria-label*='Search' i]",
                    "button[aria-label*='Search' i]",
                    ".ac-gn-searchform",
                    "#globalnav-menustate-search"
                ]
                
                for icon_selector in apple_search_icons:
                    try:
                        icon = await page.query_selector(icon_selector)
                        if icon:
                            is_visible = await icon.is_visible()
                            if is_visible:
                                await icon.click()
                                self.log(f"✅ Clicked Apple search icon: {icon_selector}")
                                await asyncio.sleep(2)  # Wait for search input to appear
                                break
                    except:
                        continue
                
                # Now try to find the search input (should be visible after clicking icon)
                apple_input_selectors = [
                    "#ac-gn-searchform-input",
                    "input.ac-gn-searchform-input",
                    "input[type='search']",
                    "input[name='q']",
                    "input[aria-label*='Search' i]"
                ]
                
                for selector in apple_input_selectors:
                    try:
                        element = await page.wait_for_selector(selector, timeout=3000, state="visible")
                        if element:
                            self.log(f"✅ Found Apple search input: {selector}")
                            return {
                                "found": True,
                                "input_selector": selector,
                                "button_selector": "button.ac-gn-searchform-submit, button[type='submit']",
                                "method": "apple_specific"
                            }
                    except:
                        continue
            
            # Strategy 1: Try common selectors directly with Playwright
            common_selectors = [
                "input[type='search']",
                "input[type='text'][name*='search' i]",
                "input[type='text'][id*='search' i]",
                "input[type='text'][placeholder*='Search' i]",
                "input[type='text'][placeholder*='search' i]",
                "input[name='q']",
                "input[name='search']",
                "input[id='search']",
                "input[id='searchbox']",
                "#search",
                "#searchbox",
                ".search input",
                ".searchbox input",
                "input[aria-label*='Search' i]",
                "input[aria-label*='search' i]",
                "form[action*='search' i] input",
                "form[method='get'] input[type='text']"
            ]
            
            for selector in common_selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=2000, state="visible")
                    if element:
                        # Get more info about the element
                        tag_name = await element.evaluate("el => el.tagName")
                        input_type = await element.evaluate("el => el.type || ''")
                        name_attr = await element.evaluate("el => el.name || ''")
                        id_attr = await element.evaluate("el => el.id || ''")
                        
                        self.log(f"✅ Found search box: {selector} (tag: {tag_name}, type: {input_type}, name: {name_attr}, id: {id_attr})")
                        
                        # Find associated button
                        button_selectors = [
                            "button[type='submit']",
                            "input[type='submit']",
                            "button.search",
                            "button[aria-label*='Search' i]",
                            "form button",
                            f"form:has({selector}) button"
                        ]
                        
                        button_selector = None
                        for btn_sel in button_selectors:
                            try:
                                btn = await page.query_selector(btn_sel)
                                if btn:
                                    button_selector = btn_sel
                                    break
                            except:
                                continue
                        
                        return {
                            "found": True,
                            "input_selector": selector,
                            "button_selector": button_selector,
                            "method": "direct_selector"
                        }
                except:
                    continue
            
            # Strategy 2: Use AI to analyze page and find search box
            try:
                page_content = await self.web_navigator.get_page_content()
                content_preview = page_content[:8000] if len(page_content) > 8000 else page_content
                
                ai_prompt = f"""
                Analyze this HTML content and find the search input field. Return a JSON object with:
                - input_selector: Exact CSS selector for the search input field
                - button_selector: CSS selector for the search/submit button (if exists)
                - method: "ai_detected"
                
                Look for:
                1. Input fields with type="search" or type="text" that are clearly for searching
                2. Inputs with name, id, or placeholder containing "search", "q", "query"
                3. Forms with action containing "search"
                4. Inputs with aria-label containing "search"
                
                HTML Content (first 8000 chars): {content_preview}
                
                Return ONLY valid JSON, no markdown, no code blocks.
                """
                
                response = await self.openai_client.chat.completions.create(
                    model=Config.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an expert at analyzing HTML and finding search elements. Always return valid JSON only."},
                        {"role": "user", "content": ai_prompt}
                    ],
                    temperature=0.1,
                    timeout=30.0
                )
                
                result_text = response.choices[0].message.content.strip()
                # Remove markdown code blocks if present
                if result_text.startswith("```"):
                    result_text = result_text.split("```")[1]
                    if result_text.startswith("json"):
                        result_text = result_text[4:]
                result_text = result_text.strip()
                
                ai_result = json.loads(result_text)
                if ai_result.get("input_selector"):
                    self.log(f"✅ AI found search box: {ai_result.get('input_selector')}")
                    return {
                        "found": True,
                        "input_selector": ai_result.get("input_selector"),
                        "button_selector": ai_result.get("button_selector"),
                        "method": "ai_detected"
                    }
            except Exception as e:
                if "429" not in str(e) and "quota" not in str(e).lower():
                    self.log(f"AI search detection failed: {str(e)[:100]}", "warning")
            
            # Strategy 3: Parse HTML with BeautifulSoup
            try:
                page_content = await self.web_navigator.get_page_content()
                soup = BeautifulSoup(page_content, 'html.parser')
                
                # Find all input elements
                inputs = soup.find_all('input', type=['text', 'search'])
                for inp in inputs:
                    name = (inp.get('name') or '').lower()
                    id_attr = (inp.get('id') or '').lower()
                    placeholder = (inp.get('placeholder') or '').lower()
                    aria_label = (inp.get('aria-label') or '').lower()
                    
                    if any(keyword in text for keyword in ['search', 'q', 'query'] 
                           for text in [name, id_attr, placeholder, aria_label]):
                        selector = f"input"
                        if inp.get('id'):
                            selector = f"#{inp.get('id')}"
                        elif inp.get('name'):
                            selector = f"input[name='{inp.get('name')}']"
                        
                        self.log(f"✅ Found search box via HTML parsing: {selector}")
                        return {
                            "found": True,
                            "input_selector": selector,
                            "button_selector": "button[type='submit'], input[type='submit']",
                            "method": "html_parsing"
                        }
            except Exception as e:
                self.log(f"HTML parsing failed: {str(e)[:100]}", "warning")
            
            return {"found": False}
        
        except Exception as e:
            self.log(f"Error in universal search box detection: {str(e)}", "error")
            return {"found": False}
    
    async def execute_search(self, search_query: str, page) -> bool:
        """Execute search using the found search box."""
        try:
            # Find search box
            search_info = await self.find_search_box_universal(page)
            
            if not search_info.get("found"):
                self.log("❌ Could not find search box on page", "error")
                return False
            
            input_selector = search_info["input_selector"]
            button_selector = search_info.get("button_selector")
            
            self.log(f"🔍 Using search box: {input_selector}")
            
            # Wait for and interact with search input
            try:
                search_input = await page.wait_for_selector(input_selector, timeout=5000, state="visible")
                if not search_input:
                    self.log(f"Search input not visible: {input_selector}", "error")
                    return False
                
                # Clear and fill
                await search_input.click()
                await asyncio.sleep(0.5)
                await search_input.fill('')  # Clear first
                await asyncio.sleep(0.3)
                await search_input.fill(search_query)
                self.log(f"✅ Typed search query: {search_query}")
                await asyncio.sleep(1)
                
                # Submit search
                submitted = False
                
                # Try button first
                if button_selector:
                    try:
                        button = await page.wait_for_selector(button_selector, timeout=2000)
                        if button:
                            await button.click()
                            self.log(f"✅ Clicked search button: {button_selector}")
                            submitted = True
                    except:
                        pass
                
                # If no button, press Enter
                if not submitted:
                    await search_input.press('Enter')
                    self.log("✅ Pressed Enter to submit search")
                    submitted = True
                
                # Wait for results
                self.log("⏳ Waiting for search results...")
                await asyncio.sleep(5)
                
                return True
                
            except Exception as e:
                self.log(f"Error executing search: {str(e)}", "error")
                return False
        
        except Exception as e:
            self.log(f"Error in execute_search: {str(e)}", "error")
            return False
    
    async def find_product_elements(self, product_specs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find product elements on the current page."""
        try:
            page_content = await self.web_navigator.get_page_content()
            current_url = await self.web_navigator.get_page_url()
            
            # Try AI first if available
            try:
                content_preview = page_content[:8000] if len(page_content) > 8000 else page_content
                
                ai_prompt = f"""
                Analyze this HTML content and find product elements that match the specifications.
                Return a JSON array of product objects, each with:
                - title: Product title/name
                - price: Product price (if visible)
                - link: Full URL to product page (make absolute if relative)
                - selector: CSS selector to click this product
                - matches_specs: true if it matches the specifications, false otherwise
                
                Product Specifications: {json.dumps(product_specs, indent=2)}
                Current URL: {current_url}
                HTML Content (preview): {content_preview}
                
                Look for:
                1. Product cards, items, or listings
                2. Links to product detail pages
                3. Product titles and prices
                4. Elements that match the product specifications
                
                Return ONLY a valid JSON array, no markdown, no code blocks.
                """
                
                response = await self.openai_client.chat.completions.create(
                    model=Config.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an expert at analyzing e-commerce pages and finding products. Always return valid JSON arrays only."},
                        {"role": "user", "content": ai_prompt}
                    ],
                    temperature=0.2,
                    timeout=30.0
                )
                
                result_text = response.choices[0].message.content.strip()
                if result_text.startswith("```"):
                    result_text = result_text.split("```")[1]
                    if result_text.startswith("json"):
                        result_text = result_text[4:]
                result_text = result_text.strip()
                
                products = json.loads(result_text)
                if isinstance(products, list) and len(products) > 0:
                    self.log(f"✅ AI found {len(products)} products")
                    return products
            except Exception as e:
                if "429" not in str(e) and "quota" not in str(e).lower():
                    self.log(f"AI product finding failed: {str(e)[:100]}", "warning")
            
            # Fallback: Parse HTML for product links
            soup = BeautifulSoup(page_content, 'html.parser')
            products = []
            
            # Look for product links
            product_keywords = ['product', 'item', 'buy', 'shop', 'detail']
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                text = link.get_text(strip=True).lower()
                
                # Check if it looks like a product link
                if any(keyword in text or keyword in href.lower() for keyword in product_keywords):
                    full_url = href if href.startswith('http') else f"{current_url.rstrip('/')}{href}"
                    products.append({
                        "title": link.get_text(strip=True),
                        "link": full_url,
                        "selector": f"a[href='{href}']",
                        "matches_specs": True,
                        "price": None
                    })
                    if len(products) >= 5:
                        break
            
            return products
        
        except Exception as e:
            self.log(f"Error finding product elements: {str(e)}", "error")
            return []
    
    async def execute(self, task: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute product search task."""
        try:
            user_query = task.get("query", "")
            
            # Step 1: Extract product specifications
            self.log("📦 Extracting product specifications...")
            product_specs = await self.extract_product_specs(user_query)
            
            # Step 2: Determine website
            self.log("🌐 Determining website...")
            website = await self.determine_website(product_specs)
            
            if not website:
                product_name_lower = (product_specs.get("product_name") or "").lower()
                if "iphone" in product_name_lower or "ipad" in product_name_lower or "mac" in product_name_lower:
                    website = "https://www.apple.com"
                    self.log(f"Using default website: {website}")
                else:
                    return {
                        "status": "error",
                        "data": {},
                        "message": "Could not determine website for the product."
                    }
            
            # Step 3: Navigate to website
            self.log(f"🌐 Navigating to: {website}")
            nav_result = await self.web_navigator.execute({
                "action": "navigate",
                "url": website
            })
            
            if nav_result["status"] != "success":
                return {
                    "status": "error",
                    "data": {},
                    "message": f"Failed to navigate to website: {website}"
                }
            
            # Step 4: Execute search
            self.log("🔍 Searching for product...")
            page = self.web_navigator.page
            if not page:
                return {
                    "status": "error",
                    "data": {},
                    "message": "Browser page not available"
                }
            
            search_query = product_specs.get("product_name", user_query)
            search_success = await self.execute_search(search_query, page)
            
            if not search_success:
                self.log("⚠️  Search box not found, trying direct navigation", "warning")
                # Fallback: try direct product page
                if "apple.com" in website.lower() and "iphone" in search_query.lower():
                    await self.web_navigator.navigate_to(f"{website}/us/shop/goto/iphone")
            
            # Step 5: Find products
            self.log("🔎 Finding products on page...")
            products = await self.find_product_elements(product_specs)
            
            # Filter matching products
            matching_products = [p for p in products if p.get("matches_specs", False)]
            result_products = matching_products if matching_products else products[:5]
            
            return {
                "status": "success",
                "data": {
                    "product_specs": product_specs,
                    "website": website,
                    "products": result_products,
                    "search_executed": search_success
                },
                "message": f"Found {len(result_products)} products"
            }
        
        except Exception as e:
            self.log(f"Error executing product search: {str(e)}", "error")
            return {
                "status": "error",
                "data": {},
                "message": str(e)
            }
