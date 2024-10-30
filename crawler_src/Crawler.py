import time
import random
import os

from playwright.sync_api import sync_playwright


class Crawler:
    """ TODO """
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.accept_words = [
            'Alles accepteren', 
            'Accept all cookies',
            'Cookies toestaan',
            'Allow all', 
            'Akkoord', 
            'Accept Cookies', 
            'Alle akzeptieren', 
            'Accept all', 
            'Accepter et fermer', 
            'Accetta e chiudi', 
            'Accetta', 
            'ACCETTA E CONTINUA', 
            'Yes, I agree', 
            'I agree', 
            'Continue']

    def search_button_or_link(self, page, word):
        # 1.1 try to find a button element
        accept_button = page.get_by_role(role="button", name=word, exact=False)  # not exact matching - TODO discuss
        # accept_button = page.locator(f"button:has-text('{word}')")
        if accept_button.count() == 1:
            print("BUTTON FOUND")
            return accept_button
        
        # try to find a span inside button
        accept_span = page.locator(f"button:has(span:text('{word}'))")
        if accept_span.count() == 1:
            print("SPAN FOUND")
            return accept_span
        
        # try to find a link alement
        accept_link = page.get_by_role(role="link", name=word, exact=True)
        if accept_link.count() == 1:
            accept_link.click()
            print("LINK FOUND")
            return accept_link

    def find_accept_element(self, page):
        # try to accept on the main page
        print("Searching on main page")
        for word in self.accept_words:
            print(word)
            accept_element = self.search_button_or_link(page, word)
            if accept_element:
                return accept_element
        print()
        print("Didn't find accept elements on the main page, iterating over frames")
        # if not found, iterate through all iframes
        for word in self.accept_words:
            print(word)
            for frame in page.frames:
                accept_element = self.search_button_or_link(frame, word)
                if accept_element:
                    return accept_element
        print("No elements found in the frames")
        return None

    def accept_cookies(self, page):
        accept_button = self.find_accept_element(page)
        if accept_button:
            print('Clicking Button')
            accept_button.click()
        else:
            print("Proceeding without accepting")
        time.sleep(3)

    def scroll_down(self, page):
        # TODO: Make the scrolling step-by-step to evade bot-detection
        for percentage in range(10, 100, 10):
            if percentage != 100:
                # To make it less robotic
                percentage += random.randint(-5, 5)
            print(f"Scrolling down to {percentage}%")
            page.evaluate(f'window.scrollTo(0, document.body.scrollHeight*{percentage/100})')
            # Just so that it looks nicer on the video, and gives more time to load things
            time.sleep(0.5)
        print(f"Scrolled down fully")
        time.sleep(3)


    def crawl(self, url):
        print("============================================================")
        print(f'Crawling {url}')

        # TODO: Implement the function to parse the URL
        with sync_playwright() as p:
            #Launch with visual browser
            url_core = url.strip()
            browser = p.chromium.launch(headless=False)
            url_type = "news" if "news" in self.output_path else "gov"
            context = browser.new_context(record_har_path=f"{self.output_path}/{url_core}_{url_type}.har",
                                          record_video_dir=f"{self.output_path}/") # new profile
            page = context.new_page()
            page.goto('https://www.'+url)
            time.sleep(10)  # TODO this has to be 10 according to the assignment
            print(f"Screenshotting {url_core}_before_cookies.png")
            page.screenshot(path=f"{self.output_path}/{url_core}_{url_type}_pre_consent.png", full_page=True)
            self.accept_cookies(page=page)
            print(f"Screenshotting {url_core}_after_cookies.png")
            page.screenshot(path=f"{self.output_path}/{url_core}_{url_type}_post_consent.png", full_page=True)
            self.scroll_down(page=page)
            # HAR files and video get saved when the context is closed
            print("Saving video and HAR files...")
            context.close()
            path = page.video.path()
            # Rename the video file in path
            os.rename(path, f"{self.output_path}/{url_core}_{url_type}.webm")
            browser.close()

            # nytimes.com - press continue to scroll through website - press 2 buttons
             # https://www.nbcnews.com/ - continue window as well