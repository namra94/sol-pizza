# Content needed

Everything the site is waiting for, what it's for and who has it. Nothing here is made
up in the meantime: a section that needs one of these is built, but kept off sol.pizza
until it arrives (`gate()` in `build/gen.py`). The full previews show it with a yellow
**Content needed** label and its key:

- **full-site**: https://full-site-sol-pizza.polarized-jar.workers.dev (what's on `main`)
- **a pull request**: `https://full-claude-<branch>-sol-pizza.polarized-jar.workers.dev`
  (the branch `claude/<branch>`, copied to `full/claude/<branch>`)

When something arrives, send it over (or put it where the table says), and the section
goes live with the next build. Every key in `backticks` below is a gated section: the
build stops if `gen.py` gates a section that isn't listed here.

Last updated 13 October 2026.

## Needed soon: before opening

| What | Where it goes | Format | Who has it |
| --- | --- | --- | --- |
| The opening date | `OPENING_DATE` near the top of `build/gen.py`: the home page, Booking, Visit, the descriptions and the opening hours in the structured data. From the opening time that day, the pages switch to "open" by themselves | `YYYY-MM-DD` | Arman |
| Last orders | `HOURS['last_orders']` in `build/gen.py`: the footer and Visit | `HH:MM` | The kitchen |
| The ResDiary widget | `RESDIARY_URL` in `build/gen.py`: the widget on `/booking/`, and contact becomes tappable everywhere (phone bar, booking box); `RESDIARY_URL_VI` if there's a separate Vietnamese widget | The widget's URL (ResDiary → Promote → Widget configurator → Embed Code), and the Vietnamese one if there is one | Host and Supervisor |
| Deposits in the widget | Whether `/booking/` must allow payments in the widget's frame (`Permissions-Policy`) | Yes or no, and which payment screen it shows | Supervisor (ResDiary) |
| Booking terms | The booking policy on `/booking/`: cancellations, deposits, how long a table is held, the largest party that can book online | A few lines, English and Vietnamese | Supervisor |
| Zalo number | `ZALO` in `build/gen.py`: the phone bar on Vietnamese pages, the booking page (from when online booking is live) | The number as Zalo shows it | Arman |
| WhatsApp number | `WHATSAPP` in `build/gen.py`: the booking page (from when online booking is live) | International, without the + (84…) | Arman |
| Inbox for enquiries | Where the private dining form, the opening-week form and the newsletter sign-up send their email (`ENQUIRIES` in `build/gen.py`) | An address (hello@sol.pizza unless you say otherwise) | Arman |
| The map pin | The Directions button and the structured data. The Google listing "Sol Hanoi" carries Sol Pizza's reviews: say whether its pin is on the new building | Latitude and longitude, or the Google Maps link to the right place | Arman |
| Holiday and Tết hours | `build/announcements.json`: the bar at the top of every page, and Visit | Dates, and a line in English and Vietnamese | Arman, Supervisor |
| Eclipse, 23–24 October | `build/events-data.json`, the first edition: `/events/` lists it with its dates now; its own page, `/events/eclipse-1/`, goes live once it has its line (`summary_en`, `summary_vi`) | A line or two on what it is, the times, guest chef(s) and a line on each, the menu, the price, how to book (a link, or by email), artwork | Arman |

## The menu

| What | Where it goes | Format | Who has it |
| --- | --- | --- | --- |
| Prices | `build/menu-data.json`: a price for each dish and drink, glass and bottle for each wine. The "A first draft" notes come off when every item has one | Whole numbers in đồng (185000) | Kitchen, bar |
| More dietary marks | `build/menu-data.json`: today Veg and Spicy; add others (vegan, gluten-free…) only once the kitchen confirms each dish | The mark, its meaning in both languages, and the dishes | Kitchen |
| The new wine list | `build/menu-data.json` (the build checks the counts in the copy) | Name, grape, producer, region, vintage, glass or bottle | Arman |

## The pages

| What | Where it goes | Format | Who has it |
| --- | --- | --- | --- |
| Private dining | `/private-dining/`: the spaces on each floor and how many each seats, set menus, minimum spend | Figures, a line on each space, English and Vietnamese | Arman |
| Large groups | Visit and Private dining: how many seats in all, the largest table | Figures | Supervisor |
| The team | `/about/`: portraits and a few lines on each person (Ngọc runs the kitchen; should "and Long runs the floor" be added?) | 2–3 lines each, English and Vietnamese, a portrait | Arman |
| The dough | `/about/`, "The dough": the flours, how long it ferments, how it's baked | A few lines, English and Vietnamese | The kitchen |
| Sol Pizza to Sol | `/about/`: one line on what closing Sol Pizza meant to you and the team | A line or two | Arman |
| The terrace | `/about/` says "a terrace for when the weather behaves": is there one? | Yes or no | Arman |
| Getting here | Visit & FAQ: motorbike and car parking, where Grab drops off, the lift and step-free access, dress code, corkage, payment methods, dogs, smoking | A line each, English and Vietnamese | Supervisor |
| Press and review quotes | The home page | The quote, who said it, where and when, and their OK to use it | Arman |
| Press contact | `PRESS_CONTACT` in `build/gen.py`: `/press/`, which is live with the facts and the logo, and says hello@sol.pizza until then | Name and email | Arman |
| Gift cards | `/gift-cards/`, built and waiting: values, how long a card lasts; how to buy is "at the restaurant, or by email" (online sales would need the Ministry of Industry and Trade notification first) | Values in đồng, how long a card lasts | Arman |
| Takeaway and delivery | An Order page, only if you want one: which apps carry Sol (the Host job description mentions ordering platforms) | App names and links | Arman |
| Social links | `SOCIAL` in `build/gen.py`: the footer and the structured data (Instagram is there) | Facebook, TikTok, Zalo OA… addresses | Arman |
| Tax code | `TAX_CODE` in `build/gen.py`: the footer, beside Công ty TNHH Aurelian; and `REGISTERED_ADDRESS` if the company's registered address isn't the restaurant's | Mã số thuế; the registered address | The accountant |
| The public name | The structured data and Google: "Sol" with "Sol Hanoi" as its other name, until you decide | Sol or Sol Hanoi | Arman |

## Photography

| What | Where it goes | Format | Who has it |
| --- | --- | --- | --- |
| Photographs: the room on each floor, the bar, the oven, the food, the team, the building from the lane | Cloudflare R2 (`media.sol.pizza`) and `build/media.json`: the home page, About, Menu, Private dining, Events, Press | sRGB JPEG, long edge 3,000–4,000 px, with a credit; alt text in English and Vietnamese for each | The photographer |
| A video for the home page (optional) | The home page's first screen, muted, with a still for phones | MP4, about 2 MB at most, and a poster frame | The photographer |

## Search

| What | Where it goes | Format | Who has it |
| --- | --- | --- | --- |
| Search Console verification | A tag in every page's head | The code Google gives | Arman |
| Payment methods | Visit and the structured data | Cash, cards (which), transfer, e-wallets | Supervisor |

## Legal

Cleared by the lawyer on 13 October 2026: the cookie banner and its notice, no age check
for the drinks pages, and the site is not an e-commerce platform (no Ministry of Industry
and Trade notification for online booking). The drinks offers stay as they are.

| What | Where it goes | Format | Who has it |
| --- | --- | --- | --- |
| The guest privacy notice's facts | `/privacy/guests/`: how long booking and enquiry details are kept, and who processes them (ResDiary, Google Workspace, Cloudflare, Adobe Fonts; Google Analytics and Meta with a yes to cookies) | Retention periods; any processor missing from the list | Arman, the lawyer |
| Allergies (health data) | `/privacy/guests/` says the team asks a guest's consent before recording an allergy or dietary need: is that how it will work, and is that consent enough under Law 91/2025? | Yes or what to change | Arman, the lawyer |

## Gated sections

Each key below is a section the public build leaves out until its content arrives.

| Key | What it waits for |
| --- | --- |
| `booking-terms` | `/booking/`, "Before you book": cancellations, deposits, how long a table is held, the largest party that can book online (Booking terms, above) |
| `private-dining-spaces` | `/private-dining/`, "The spaces": each floor and the whole restaurant, and how many each seats (Private dining, above) |
| `private-dining-menus` | `/private-dining/`, "Set menus": menus for groups and their prices |
| `private-dining-minimum` | `/private-dining/`, "Minimum spend" for a private space |
| `visit-last-orders` | `/visit-us/`, under the hours: last orders (Last orders, above) |
| `visit-capacity` | `/visit-us/`, Good to know, "Big groups": how many seats in all, the largest table (Large groups, above) |
| `visit-getting-here` | `/visit-us/`, "Getting here and parking": motorbike and car parking, where Grab drops off (Getting here, above) |
| `visit-access` | `/visit-us/`, "Step-free access and the lift": the lift, steps, the toilets (Getting here, above) |
| `visit-payment` | `/visit-us/`, "Paying": cash, which cards, transfer, e-wallets (Payment methods, above) |
| `visit-corkage` | `/visit-us/`, "Bringing your own wine": whether guests can, and the corkage fee (Getting here, above) |
| `visit-dress` | `/visit-us/`, "What to wear": whether there's a dress code (Getting here, above) |
| `visit-dogs` | `/visit-us/`, "Dogs": whether dogs are welcome, inside or out (Getting here, above) |
| `visit-smoking` | `/visit-us/`, "Smoking": whether there's anywhere to smoke (Getting here, above) |
| `about-closing` | `/about/`, Sol Pizza: a line or two on what closing it meant to you and the team (Sol Pizza to Sol, above) |
| `about-dough` | `/about/`, "The dough": its flours, how long it ferments, how it's baked, in the kitchen's words |
| `about-team` | `/about/`, "The team": a portrait and two or three lines on each person (The team, above) |
| `company-tax-code` | The footer's last line: the tax code (`TAX_CODE` in `build/gen.py`; Tax code, above) |
| `press-contact` | `/press/`, "Who to ask": a name and an email (`PRESS_CONTACT`; Press contact, above). Until then it says hello@sol.pizza |
| `press-photos` | `/press/`: approved photographs to download, with their credits (Photography, above) |
| `home-press` | The home page: press or review quotes (Press and review quotes, above) |
| `event-<slug>` | The whole page of each Eclipse edition, `/events/<slug>/` (today `event-eclipse-1`): its line (Eclipse, above). It goes live by itself once `summary_en` and `summary_vi` are in `build/events-data.json`; a new edition needs nothing here |
| `gift-cards` | The whole page `/gift-cards/`: the values, how long a card lasts, how to buy one (Gift cards, above). To publish it, delete its line in `WAITING` in `build/gen.py` |
| `legal-guest-privacy` | The whole page `/privacy/guests/`, the guest privacy notice: the lawyer's approval, and the retention periods (Legal, above). Then delete its line in `WAITING` |
| `legal-accessibility` | The whole page `/accessibility/`, the accessibility statement: the lawyer's approval, and the building's access facts (Getting here, above). Then delete its line in `WAITING` |
