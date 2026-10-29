# Manual tests

What the automatic checks (`npm run check`) can't do: real phones, the browsers inside
Zalo, Facebook and Instagram, a screen reader, paper. Do these on sol.pizza after a big
change, and before opening. Each takes a few minutes. Tick what works; for anything that
doesn't, note the phone, the app and the page.

Start each with a **fresh visit**: a private tab, or clear the site's data (iPhone:
Settings → Apps → Safari (before iOS 18: Settings → Safari) → Advanced → Website Data →
sol.pizza → Delete).

## 1. iPhone, Safari

- [ ] `sol.pizza`: the cookie banner sits at the foot. **Reject all**: it goes, and the
      phone bar appears (Book · Directions). Reload: no banner.
- [ ] Scroll the home page: nothing jumps as it loads; the bar at the foot stays.
- [ ] **VI** (top left): the page in Vietnamese at `sol.pizza/vi/`. In the same tab, type
      `sol.pizza` again: it opens in Vietnamese. **EN**: back to English.
- [ ] The menu button (top right): the menu opens over the page; **Menu**, **Events**,
      **Visit**… each opens its page; the × closes it.
- [ ] **Book** in the phone bar: the booking page. Before online booking: the phone
      number and email are text to copy (press and hold). Once ResDiary is live: the
      booking form loads, and a test booking goes through (cancel it after).
- [ ] **Directions**: Google Maps (the app, or the website) opens with the way to Sol.
      Check the pin is on the new building.
- [ ] `/private-dining/`: fill the form, **Send by email**: Mail opens with the message
      ready, to hello@sol.pizza. The message is also on the page below the form. (Don't
      send it, or send it to yourself.)
- [ ] The footer's **Sign up by email**: Mail opens with "Please add this email address…".
- [ ] Turn the phone sideways: nothing hides behind the notch.
- [ ] Larger text: in Safari, the page menu (**aA** in the address bar) → the larger **A**
      three times (to 150%): the pages still read well, nothing overlaps.

## 2. Android, Chrome

- [ ] The same as the iPhone: the banner, VI and EN, the menu, Book, Directions, a form,
      the newsletter.
- [ ] The phone's back button after opening the menu: you go back a page (that's
      expected); the menu isn't stuck open when you return.
- [ ] Once open: the home page says "Open today, 5pm–11pm" (or "Closed today" on a
      Monday).

## 3. Inside Zalo, Facebook and Instagram

Send yourself a link to `https://sol.pizza/menu/` and to `https://sol.pizza/vi/` in each
app (a Zalo chat, a Facebook message, an Instagram message), and open it there.

- [ ] The preview in the chat shows the share card (the right language for `/vi/`).
- [ ] The page opens inside the app; the cookie banner works; **Book** and **Directions**
      work.
- [ ] A form's **Send by email**: these apps often don't open Mail. The message then
      appears on the page to copy, with hello@sol.pizza: check that it does.
- [ ] Instagram: the link in the profile's bio opens the right page.

## 4. Keyboard only (a laptop)

Put the mouse away; Tab moves forward, Shift+Tab back, Enter or Space presses.

- [ ] On a fresh visit, the first Tab shows **Skip to content**; the next ones reach the
      cookie banner's links and buttons, then the header. **Reject all** with Enter.
- [ ] Every link and button shows a clear outline when it has the focus, and nothing
      with the focus hides behind the cookie banner or the bar at the top.
- [ ] Narrow the window below 1,024 px: the menu button opens the menu with Enter, and
      Esc closes it, the focus back on the button.
- [ ] `/private-dining/`: fill the form and send it with the keyboard alone.
- [ ] The footer's **Cookie settings** opens the choices again.

## 5. VoiceOver, a spot check (iPhone)

Settings → Accessibility → VoiceOver (or ask Siri "turn on VoiceOver"). Swipe right to
move, double-tap to press.

- [ ] The home page: the logo reads "Sol, home"; the headings come in order; the cookie
      banner reads as one region with its three buttons.
- [ ] `/vi/`: VoiceOver reads in its Vietnamese voice.
- [ ] `/menu/` (once priced): each dish reads its name, then its price.
- [ ] A form: each field reads its label (and "optional" where it is); after **Send by
      email**, VoiceOver reads the message about your email app.
- [ ] Photos (once they're in): each reads its description, in the page's language.

## 6. The menu on paper

- [ ] `/menu/`, `/menu/wine/`, `/menu/bar/`: Print (or Save as PDF). The logo at the top;
      no bars, banners or buttons; sections not split across pages where it can be
      helped; the prices (once set) line up.

## 7. The back office, on a phone (iPhone and Android)

`sol.pizza/backoffice/`, with the staff password. What goes to Slack is real: make the
note **TEST — ignore**, and react ❌ to it in #supply afterwards.

- [ ] Signed out, `sol.pizza/backoffice/purchase/` opens the sign-in page. A wrong
      password: "That isn't the password". The staff password: straight on to the form.
- [ ] **Requested by** lists the team; pick a name. Reload the page: it's still picked.
- [ ] **Supplier**: Active ones first, then Quoting, then Not used yet; no Stopped one.
      Picking one shows who orders it, its order days and cut-off, and picks its station.
- [ ] **Items**: type part of an item in Vietnamese without the accents ("pho mai"): the
      list finds it. Pick it: its unit fills in, and its price and the line's estimate
      show under it. Type something that isn't on the list: "not in the Order Guide — no
      price". **Thêm hàng** adds a row, **Xóa** takes one away.
- [ ] The summary: the estimate before VAT and who approves. Over 5,000,000đ, or with
      **Other supplier…**: the line "Arman's ✅ needed".
- [ ] **VI** (top left): every label in Vietnamese, prices as 1.250.000đ.
- [ ] **Preview the message**: the 🛒 block. Change a quantity: the preview goes away.
      Preview again, then **Send to #supply**: "Sent to #supply" and a ref. In #supply,
      the message, mentioning the right people. React ❌.
- [ ] Turn on airplane mode and send another (TEST — ignore): "Couldn't send it", and
      everything typed is still there. Airplane mode off, send again: it arrives once.
- [ ] **Recent requests**: both, "Sent to Slack".
- [ ] **Sign out**: the sign-in page. `sol.pizza/dough/` still asks for the kitchen password.

## Once ResDiary is live

- [ ] `/booking/` and `/vi/booking/`: the widget loads in both (in Vietnamese on `/vi/` if
      ResDiary has a Vietnamese widget, `RESDIARY_URL_VI`).
- [ ] With deposits: a test booking reaches the payment step, and it works inside the
      page.
- [ ] Under the widget, "Trouble with the booking form?" with the phone, Zalo and email.
- [ ] The phone bar: **Call** on English pages, **Zalo** on Vietnamese ones (once
      `ZALO` is set), and both open the right app.
