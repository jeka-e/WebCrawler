import time

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
        # Works but... maybe we need to scroll slower to capture more data?
        # Now it's just a quick jump to the bottom of the page.
        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        time.sleep(3)


    def crawl(self, url):
        print("============================================================")
        print(f'Crawling {url}')

        # TODO: Implement the function to parse the URL
        with sync_playwright() as p:
            #Launch with visual browser
            url_core = url.split('\\')[0].strip().replace('.', '_')
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(record_har_path=f"har_files/output_har_{url_core}.json",
                                          record_video_dir="videos/") # new profile
            page = context.new_page()
            page.goto('https://www.'+url)
            time.sleep(10)  # TODO this has to be 10 according to the assignment
            url_core = url.split('\\')[0].strip().replace('.', '_')
            page.screenshot(path=f"screenshots/{url_core}_before_cookies.png")
            self.accept_cookies(page=page)
            page.screenshot(path=f"screenshots/{url_core}_after_cookies.png")
            self.scroll_down(page=page)

            context.close()
            browser.close()

            # nytimes.com - press continue to scroll through website - press 2 buttons
             # https://www.nbcnews.com/ - continue window as well