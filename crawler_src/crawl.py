
from playwright.sync_api import sync_playwright
import time

from argparse import ArgumentParser

def parse_url(url):
    # TODO: Implement the function to parse the URL
    with sync_playwright() as p:
        #Launch with visual browser
        browser = p.chromium.launch(headless=False)
        context = browser.new_context() # new profile
        page = context.new_page()
        page.goto('https://www.'+url)
        print(page.title())
        time.sleep(5)  # TODO this has to be 10 according to the assignment
        accept_words = ['Alles accepteren', 'Accept all cookies', 'Cookies toestaan', 'Allow all', 'Akkoord', 'Accept Cookies', 'Alle akzeptieren', 
                        'Accept all', 'Accepter et fermer', 'Accetta e chiudi', 'Accetta', 'ACCETTA E CONTINUA', 'Yes, I agree', 'I agree']
        # accept_words = ['Accept All']
        for word in accept_words:
            print(word)
            # Try to locate the accept button 
            # Find the accept link
            # try:
            accept_button = page.get_by_role(role="button", name=word)
            accept_link = page.get_by_role(role="link", name=word)
            accept_text = page.get_by_text(word, exact=True)
            # accept_button = page.get_by_role("button", name="Accept Cookies")
            # accept_loc = page.locator(text=word)  
            accept_loc = page.locator(f'button:text("{word}")')
            print(f'BUTTON: {accept_button.count()}')
            print(f'LINK: {accept_link.count()}')
            print(f'TEXT: {accept_text.count()}')
            print(f'LOC: {accept_loc.count()}')

            if accept_button.count() > 0:
                print('PRESSING THE BUTTON')
                accept_button.click()
                break
            elif accept_link.count() > 0:
                print('PRESSING THE LINK')
                accept_link.click()
                break

            # except:
            #     continue
        time.sleep(2)
        browser.close()

        # nytimes.com - press continue to scroll through website - press 2 buttons
        # https://www.nbcnews.com/ - continue window as well
        
        

parser = ArgumentParser()
parser.add_argument("-u", "--url", dest="url", default=None,
                    help="single URL to parse", metavar="URL")
parser.add_argument("-l", "--list_url", dest="url_list", default=[],
                    help="list of URLs to parse", metavar="URLLIST")

args = parser.parse_args()

if __name__ == "__main__":
    if args.url:
        parse_url(args.url)

    elif args.url_list:
        f = open(args.url_list, 'r')
        urls = f.readlines()
        f.close()
        for url in urls:
            print(url)
            parse_url(url)
            
    else:
        print('No URL provided')
