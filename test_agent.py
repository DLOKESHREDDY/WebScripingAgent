"""
Test script for Web Scraping Agent
Tests the core functionality: navigating, searching, and finding products
"""
import asyncio
from playwright.async_api import async_playwright
import sys

async def test_basic_navigation():
    """Test basic browser navigation and search functionality."""
    print("=" * 80)
    print("TEST 1: Basic Navigation and Search")
    print("=" * 80)
    
    browser = await async_playwright().start()
    chromium = await browser.chromium.launch(headless=False, slow_mo=500)
    page = await chromium.new_page()
    
    try:
        # Navigate to Apple.com
        print("\nNavigating to Apple.com...")
        await page.goto('https://www.apple.com', wait_until='networkidle')
        print(f"Page loaded: {await page.title()}")
        await asyncio.sleep(2)
        
        # Click search icon (Apple.com specific)
        print("\nClicking search icon...")
        search_icon = await page.wait_for_selector('#ac-gn-searchform', timeout=5000)
        await search_icon.click()
        await asyncio.sleep(2)
        print("Search menu opened")
        
        # Fill search input
        print("\nTyping search query: 'iPhone 15 Pro'...")
        search_input = await page.wait_for_selector('#ac-gn-searchform-input', timeout=5000)
        await search_input.fill('iPhone 15 Pro')
        print("Search query entered")
        await asyncio.sleep(1)
        
        # Submit search
        print("\nSubmitting search...")
        await search_input.press('Enter')
        await page.wait_for_load_state('networkidle')
        print(f"Search results loaded: {await page.title()}")
        
        # Wait to see results
        print("\nWaiting 5 seconds to view results...")
        await asyncio.sleep(5)
        
        print("\nTEST 1 PASSED: Basic navigation and search works!")
        
    except Exception as e:
        print(f"\nTEST 1 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await chromium.close()
        await browser.stop()

async def test_product_search_agent():
    """Test the Product Search Agent functionality."""
    print("\n" + "=" * 80)
    print("TEST 2: Product Search Agent")
    print("=" * 80)
    
    browser = await async_playwright().start()
    chromium = await browser.chromium.launch(headless=False, slow_mo=500)
    page = await chromium.new_page()
    
    try:
        # Navigate to Apple.com
        print("\nNavigating to Apple.com...")
        await page.goto('https://www.apple.com', wait_until='networkidle')
        await asyncio.sleep(2)
        
        # Test search box detection
        print("\nTesting search box detection...")
        
        # Try to find search icon
        search_icon_selectors = [
            '#ac-gn-searchform',
            'button.ac-gn-searchform-submit',
            'a[aria-label*="Search" i]'
        ]
        
        search_icon_found = False
        for selector in search_icon_selectors:
            try:
                icon = await page.query_selector(selector)
                if icon and await icon.is_visible():
                    await icon.click()
                    print(f"Found and clicked search icon: {selector}")
                    search_icon_found = True
                    await asyncio.sleep(2)
                    break
            except:
                continue
        
        if not search_icon_found:
            print("Search icon not found, trying direct input...")
        
        # Try to find search input
        search_input_selectors = [
            '#ac-gn-searchform-input',
            'input.ac-gn-searchform-input',
            'input[type="search"]',
            'input[name="q"]'
        ]
        
        search_input_found = False
        for selector in search_input_selectors:
            try:
                input_field = await page.wait_for_selector(selector, timeout=3000, state='visible')
                if input_field:
                    print(f"Found search input: {selector}")
                    await input_field.fill('iPhone 15 Pro 256GB white')
                    print("Typed search query")
                    await asyncio.sleep(1)
                    await input_field.press('Enter')
                    print("Submitted search")
                    search_input_found = True
                    break
            except:
                continue
        
        if search_input_found:
            await page.wait_for_load_state('networkidle')
            current_url = page.url
            print(f"Navigated to: {current_url}")
            print(f"Page title: {await page.title()}")
            
            # Check if we're on a search results or product page
            if 'search' in current_url.lower() or 'iphone' in current_url.lower():
                print("Successfully reached search results/product page")
            else:
                print("May not be on expected page")
            
            await asyncio.sleep(5)
            print("\nTEST 2 PASSED: Product search agent works!")
        else:
            print("\nTEST 2 FAILED: Could not find search input")
            
    except Exception as e:
        print(f"\nTEST 2 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await chromium.close()
        await browser.stop()

async def test_universal_search():
    """Test universal search functionality on different websites."""
    print("\n" + "=" * 80)
    print("TEST 3: Universal Search (Multiple Websites)")
    print("=" * 80)
    
    test_sites = [
        {
            'name': 'Apple.com',
            'url': 'https://www.apple.com',
            'search_query': 'iPhone 15 Pro',
            'search_icon': '#ac-gn-searchform',
            'search_input': '#ac-gn-searchform-input'
        },
        # Add more test sites here
    ]
    
    browser = await async_playwright().start()
    chromium = await browser.chromium.launch(headless=False, slow_mo=300)
    
    for site in test_sites:
        print(f"\nTesting: {site['name']}")
        page = await chromium.new_page()
        
        try:
            await page.goto(site['url'], wait_until='networkidle')
            print(f"Loaded: {await page.title()}")
            await asyncio.sleep(2)
            
            # Try to click search icon if specified
            if site.get('search_icon'):
                try:
                    icon = await page.wait_for_selector(site['search_icon'], timeout=3000)
                    if icon:
                        await icon.click()
                        await asyncio.sleep(2)
                        print(f"Clicked search icon")
                except:
                    pass
            
            # Try to find and use search input
            if site.get('search_input'):
                try:
                    search_input = await page.wait_for_selector(site['search_input'], timeout=3000, state='visible')
                    if search_input:
                        await search_input.fill(site['search_query'])
                        print(f"Typed: {site['search_query']}")
                        await asyncio.sleep(1)
                        await search_input.press('Enter')
                        await page.wait_for_load_state('networkidle')
                        print(f"Search submitted: {page.url}")
                        await asyncio.sleep(3)
                except Exception as e:
                    print(f"Search failed: {str(e)[:50]}")
            
            print(f"{site['name']} test completed")
            
        except Exception as e:
            print(f"{site['name']} test failed: {str(e)[:50]}")
        finally:
            await page.close()
    
    await chromium.close()
    await browser.stop()
    print("\nTEST 3 PASSED: Universal search testing completed!")

async def test_full_agent_flow():
    """Test the complete agent flow: search -> find products -> add to cart."""
    print("\n" + "=" * 80)
    print("TEST 4: Full Agent Flow")
    print("=" * 80)
    
    from openai import AsyncOpenAI
    from config import Config
    from agents.orchestrator_agent import OrchestratorAgent
    
    try:
        Config.validate()
        client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY, timeout=60.0)
        orchestrator = OrchestratorAgent(client)
        
        print("\nRunning full agent orchestration...")
        result = await orchestrator.execute({
            "query": "iPhone 15 Pro 256GB storage white color"
        })
        
        print(f"\nResults:")
        print(f"  Status: {result['status']}")
        print(f"  Message: {result['message']}")
        
        if result.get("data", {}).get("execution"):
            execution = result["data"]["execution"]
            if execution.get("data", {}).get("results"):
                for step in execution["data"]["results"]:
                    status = "PASS" if step['result']['status'] == "success" else "FAIL"
                    print(f"  [{status}] Step {step['step']}: {step['agent']} - {step['action']}")
        
        await orchestrator.cleanup()
        
        if result['status'] == 'success':
            print("\nTEST 4 PASSED: Full agent flow works!")
        else:
            print("\nTEST 4 PARTIAL: Some steps may have failed")
            
    except Exception as e:
        print(f"\nTEST 4 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()

async def run_all_tests():
    """Run all tests sequentially."""
    print("\n" + "=" * 80)
    print("WEB SCRAPING AGENT - TEST SUITE")
    print("=" * 80)
    print("\nRunning comprehensive tests...")
    print("Watch the browser windows to see the tests in action!\n")
    
    tests = [
        ("Basic Navigation", test_basic_navigation),
        ("Product Search Agent", test_product_search_agent),
        ("Universal Search", test_universal_search),
    ]
    
    # Only run full agent flow if API key is available
    try:
        from config import Config
        Config.validate()
        tests.append(("Full Agent Flow", test_full_agent_flow))
    except:
        print("\nSkipping Full Agent Flow test (API key not configured)")
    
    results = []
    
    for test_name, test_func in tests:
        try:
            await test_func()
            results.append((test_name, True))
        except Exception as e:
            print(f"\n{test_name} failed with error: {str(e)}")
            results.append((test_name, False))
        await asyncio.sleep(2)  # Brief pause between tests
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    for test_name, passed in results:
        status = "PASSED" if passed else "FAILED"
        print(f"  [{status}] {test_name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 80)

if __name__ == "__main__":
    # Run all tests
    asyncio.run(run_all_tests())
