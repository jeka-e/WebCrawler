import time
import random
import os

from playwright.sync_api import sync_playwright


class Crawler:
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.accept_words = [
            'Alles accepteren', 
            # 'Accept all cookies',
            'Cookies toestaan',
            'Allow all', 
            'Akkoord', 
            'Accept Cookies', 
            'Alle akzeptieren', 
            'Accept all', 
            'Accepter et fermer', 
            'Accetta e chiudi', 
            'Accetta', 
            # 'ACCETTA E CONTINUA', 
            'I agree', 
            # 'Yes, I agree', 
            'Continue']
        self.load_times = {}

    def search_button_or_link_or_span(self, page, word):
        accept_elements = []
        # 1.1 try to find a button element
        accept_button = page.get_by_role(role="button", name=word, exact=False)  # not exact matching - TODO discuss
        # accept_button = page.locator(f"button:has-text('{word}')")
        if accept_button.count() == 1:
            print("BUTTON FOUND")
            accept_elements.append(accept_button)
            # return accept_button
        
        # try to find a span inside button
        accept_span = page.locator(f"button:has(span:text('{word}'))")
        if accept_span.count() == 1:
            print("SPAN FOUND")
            accept_elements.append(accept_span)
            # return accept_span
        
        # try to find a link alement
        accept_link = page.get_by_role(role="link", name=word, exact=True)
        if accept_link.count() == 1:
            accept_link.click()
            print("LINK FOUND")
            accept_elements.append(accept_link)
            # return accept_link
        return accept_elements

    def find_accept_element(self, page):
        # iterate through all iframes in reverse order, needed for some popups
        print("Searching in frames")
        accept_elements_for_all_words =  []
        for word in self.accept_words:
            print(word)
            for frame in page.frames[::-1]:
                accept_elements = self.search_button_or_link_or_span(frame, word)
                # if accept_elements:
                accept_elements_for_all_words.extend(accept_elements)
        return accept_elements_for_all_words


    def accept_cookies(self, page):
        accept_buttons = self.find_accept_element(page)
        if accept_buttons:
            for accept_button in accept_buttons:
                print('Clicking Button')
                if accept_button.is_visible():
                    accept_button.click()
                    time.sleep(0.5)
        else:
            print("Proceeding without accepting")
        time.sleep(3)

    def scroll_down(self, page):
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

    def close_pop_ups(self, page):
        overlay = page.locator("div[role='dialog'], div.modal, div.overlay, div.popup")
        if overlay.count() > 0:
            close_button = page.locator(
                "button.modal__close-button, button[role='button']:has-text('Close')"
            )
            if close_button.is_visible():
                close_button.click()
                print("Pop-up closed successfully.")
            else:
                print("Close button not found or not visible.")


    def crawl(self, url):
        print("============================================================")
        print(f'Crawling {url}')

        with sync_playwright() as p:
            #Launch with visual browser
            url_core = url.strip()
            browser = p.chromium.launch(headless=False)
            url_type = "news" if "news" in self.output_path else "gov"
            context = browser.new_context(record_har_path=f"{self.output_path}/{url_core}_{url_type}.har",
                                          record_video_dir=f"{self.output_path}/") # new profile
            page = context.new_page()

            start_time = time.time()
            if (url_core == "ouest-france.fr"):
                page.goto('https://www.'+url)
            else:
                page.goto('https://'+url)
            end_time = time.time()

            page_load_time = end_time - start_time
            print(f"Page load time: {page_load_time}")
            self.load_times[url_core] = page_load_time

            time.sleep(10)
            print(f"Screenshotting {url_core}_before_cookies.png")
            page.screenshot(path=f"{self.output_path}/{url_core}_{url_type}_pre_consent.png", full_page=True)

            self.accept_cookies(page=page)
            self.close_pop_ups(page=page)

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
        