How to install and run the crawler

1. pip3 install -r requirements.txt
2. playwright install
 # after that "playwright install", TODO put in

Crawler does:
- 

Info to collect:
- HAR file
- screenshot before and after accepting cookies
- video of visit
- page load time (before and after accepting cookies)


Problems:
- The accept cookies button often can't be identified by 'button' role, it can be a link or a span. But we want to search by role because we don't to just click on text. Solution - look for button or link with not exact match and hope the necessary text is mentioned somewhere in the element.
- the usual Playwright search doesn't search through iframes