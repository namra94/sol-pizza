# Vietnamese changes for review — Printed menu build

For Linh. Every Vietnamese line this build adds or changes, page by page: page · English · old VI · new VI. 111 lines, plus 11 dish and drink names that now stay as written. Anything not listed here is the Vietnamese the site already had.

- **Old VI** is what the live site said before this build. “—” means there was no Vietnamese (a new line, or the old site showed English only). Where the English line itself changed, the old English is noted in brackets.
- Lines marked “in the source, never shown” were written in the old generator but never reached a page.
- To change a line, edit it in `build/gen.py` (or `build/menu-data.json` for the menu), in the `t('English', 'Tiếng Việt')` pair, and rebuild.
- Not listed: typographic-only changes (straight to curly quotes, dash spacing), and the applicant privacy notice, whose text is unchanged.

## Role pages: titles and descriptions that fit search results, 13 Nov 2026

The build listed one title over 60 characters and eight descriptions over 160 on the role pages (Google shortens those). The English descriptions now give the figures in millions, as the Vietnamese ones already did. In Vietnamese, one role’s name is long enough to need it: where the whole would be too long, the name drops the English in brackets, as the role’s card on /vi/jobs/ already does. No new words.

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| /vi/jobs/kitchen-porter/ | browser tab (and the page’s name in the breadcrumb search engines read) | Nhân viên rửa bát & vệ sinh bếp (Kitchen Porter) — Sol, Tây Hồ | Nhân viên rửa bát & vệ sinh bếp — Sol, Tây Hồ |
| /vi/jobs/kitchen-porter/ | meta description | Tuyển Nhân viên rửa bát & vệ sinh bếp (Kitchen Porter) tại Sol, Tây Hồ, Hà Nội. Lương cơ bản 6,5–7,5 triệu + phí phục vụ ước tính 2–4 triệu/tháng. Hạn nộp 14/11/2026. | Tuyển Nhân viên rửa bát & vệ sinh bếp tại Sol, Tây Hồ, Hà Nội. Lương cơ bản 6,5–7,5 triệu + phí phục vụ ước tính 2–4 triệu/tháng. Hạn nộp 14/11/2026. |

## One page for privacy and cookies, 13 Nov 2026

The cookie notice (`/vi/privacy/cookies/`) is now on the privacy page, `/vi/privacy/`, under the applicant privacy notice, at `#cookies`, and the old address leads there. Both notices are word for word as they were, with their tables and their “Cập nhật lần cuối” dates (checked by comparing every piece of text on the old pages with the new one, in both languages). One link changed where it goes, not its words: in the cookie notice’s Câu hỏi, “thông báo bảo mật dành cho ứng viên” now goes to that notice’s heading higher up the same page, where it used to open the page again.

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| every page, the footer | Privacy & cookies: one link, where there were two (Privacy · Cookies) | Bảo mật · Cookie | Bảo mật & cookie |
| /vi/privacy/cookies/ | browser tab: Cookies — Sol | Cookie — Sol | — (the page is /vi/privacy/, whose tab is unchanged: Thông báo bảo mật dành cho ứng viên — Sol) |
| /vi/privacy/cookies/ | meta description: What sol.pizza keeps in your browser, and how to change your choice. | Những gì sol.pizza lưu trong trình duyệt của bạn, và cách thay đổi lựa chọn. | — |
| in the source, never shown | the footer once the guest privacy notice was public: Privacy · Applicant privacy | Quyền riêng tư · Bảo mật cho ứng viên | — (the guest notice will join /vi/privacy/ as a section, and the footer keeps its one link) |

Question for Linh:

6. **“Bảo mật & cookie”**, the footer’s one link to the privacy page (the two links were “Bảo mật” and “Cookie”): is “&” right in a footer, or would “Bảo mật và cookie” read better?

## One page for booking, Visit and private dining, 13 Nov 2026

Visit (`/vi/visit-us/`) and Private dining (`/vi/private-dining/`) are no longer pages of their own: they are the second and third parts of the booking page, `/vi/booking/`, under the booking box, and the old addresses lead there. **No Vietnamese line is new, and none changed.** Every line of the two old pages is on the booking page word for word (checked by comparing every piece of text on the three old pages with the new one, in both languages): “Ghé thăm · Tìm chúng tôi · Sol nằm ở hai tầng đầu của tòa nhà số 7, ngõ 88 Quảng An. Chúng tôi sắp khai trương.” and “Tiệc riêng · Nhóm đông và tiệc riêng · Từ bảy người trở lên, hay một buổi tối chỉ dành riêng cho bạn…” now open their parts of the page as headings, where they were page titles. In the header, “Ghé thăm” leads to that part of the booking page and “Tiệc riêng” is no longer a tab; it is still in the footer and on the home page’s card.

These lines left the site, because the merge made them redundant or their page is gone:

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| /vi/visit-us/ | the box at the end: Book a table (heading and button), with the “Seven or more?” line | Đặt bàn · Nhóm từ bảy người trở lên? Hãy cho chúng tôi biết về nhóm của bạn, chúng tôi sẽ sắp xếp riêng. | — (the booking box is now at the top of the same page; the “Seven or more?” line is still in it, unchanged) |
| /vi/booking/ | the closing line: Tuesday to Sunday, 5pm–11pm, from the day we open · No 7, Lane 88 Quang An Street, Tây Hồ, Hanoi · Hours, address and getting here | Thứ Ba đến Chủ Nhật, 17:00 – 23:00, kể từ ngày khai trương · Số 7, Ngõ 88 Quảng An, Tây Hồ, Hà Nội · Giờ mở cửa, địa chỉ và đường đến | — (Visit’s hours and address are just below it now) |
| /vi/visit-us/ | browser tab: Visit — Sol, Tây Hồ | Ghé thăm — Sol, Tây Hồ | — (the page is /vi/booking/: Đặt bàn — Sol, Tây Hồ) |
| /vi/visit-us/ | meta description: Sol is at No 7, Lane 88 Quang An Street, Tây Hồ, Hanoi. Open Tuesday to Sunday, 5pm–11pm, from the day we open. | Sol ở số 7, ngõ 88 Quảng An, Tây Hồ, Hà Nội. Mở cửa Thứ Ba đến Chủ Nhật, 17:00 – 23:00, kể từ ngày khai trương. | — (the booking page’s, unchanged: Số 7, ngõ 88 Quảng An, Tây Hồ, Hà Nội. Thứ Ba đến Chủ Nhật, 17:00 – 23:00, kể từ ngày khai trương. Đặt bàn trực tuyến, hoặc gọi điện hay gửi email.) |
| /vi/private-dining/ | browser tab: Private dining — Sol, Tây Hồ | Tiệc riêng — Sol, Tây Hồ | — |
| /vi/private-dining/ | meta description: Groups of seven or more and private dining at Sol, No 7, Lane 88 Quang An, Tây Hồ, Hanoi. Tell us what you have in mind. | Nhóm từ bảy người trở lên và tiệc riêng tại Sol, số 7, ngõ 88 Quảng An, Tây Hồ, Hà Nội. Hãy cho chúng tôi biết bạn muốn tổ chức thế nào. | — |
| /vi/private-dining/ | share card: Private dining · Tây Hồ, Hanoi · Groups and private dining. | Tiệc riêng · Tây Hồ, Hà Nội · Nhóm đông và tiệc riêng. | — (retired: the booking page keeps its card, Tây Hồ, Hà Nội · Tìm chúng tôi và đặt bàn.) |
| in the source, never shown | Seven or more? Email us and we’ll look after you personally. (for a booking page without the enquiry form, which can’t happen on one page) | Nhóm từ bảy người trở lên: vui lòng gửi email, chúng tôi sẽ sắp xếp riêng cho bạn. | — |

## The back office: Google Chat, 12 Nov 2026

The team moves from Slack to Google Chat on Friday 13 November, so purchase requests now go to Google Chat, to the space “Sol · Supply”. Every back-office line that said Slack says Google Chat, and #supply is Supply: “kênh #supply” became “không gian Supply”. Nothing else in these lines changed, and the 📝 message’s own lines are exactly as they were. The two back-office sections below (31 Oct, 29 Oct) keep the lines that stay as they were; the ones that changed are here, with what they said before. The old English is in brackets.

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| /backoffice/ | Purchase request · Ask for the items you need. Management approves it in Google Chat and chooses the supplier and brand. (was: … approves it in Slack and chooses …) | Ghi những mặt hàng cần mua. Quản lý duyệt trên Slack rồi chọn nhà cung cấp và thương hiệu. | Ghi những mặt hàng cần mua. Quản lý duyệt trên Google Chat rồi chọn nhà cung cấp và thương hiệu. |
| /backoffice/ | Recent requests · The last 30, and whether each one reached Google Chat. (was: … reached Slack.) | 30 yêu cầu gần nhất, và yêu cầu nào đã lên Slack. | 30 yêu cầu gần nhất, và yêu cầu nào đã lên Google Chat. |
| /backoffice/purchase/ | lead: Ask for supplies. Management approves it in Google Chat, in Supply, then chooses the supplier and brand. (was: … in Slack, in #supply, then …) | Đề nghị mua hàng. Quản lý duyệt trên Slack, trong kênh #supply, rồi chọn nhà cung cấp và thương hiệu. | Đề nghị mua hàng. Quản lý duyệt trên Google Chat, trong không gian Supply, rồi chọn nhà cung cấp và thương hiệu. |
| /backoffice/purchase/ | meta description: Ask for supplies: the request goes to Google Chat, where management approves it and chooses the supplier and brand. (was: … goes to Slack, where …) | Đề nghị mua hàng: yêu cầu được gửi lên Slack để quản lý duyệt rồi chọn nhà cung cấp và thương hiệu. | Đề nghị mua hàng: yêu cầu được gửi lên Google Chat để quản lý duyệt rồi chọn nhà cung cấp và thương hiệu. |
| /backoffice/purchase/ | Dry run: requests are kept here but not posted to Google Chat. (was: … not posted to Slack.) | Chạy thử: yêu cầu được lưu ở đây nhưng không đăng lên Slack. | Chạy thử: yêu cầu được lưu ở đây nhưng không đăng lên Google Chat. |
| /backoffice/purchase/ | above Preview: Management approves it in Google Chat, then orders it from the supplier and brand they choose. (was: … approves it in Slack, then …) | Quản lý duyệt trên Slack, rồi đặt hàng với nhà cung cấp và thương hiệu do quản lý chọn. | Quản lý duyệt trên Google Chat, rồi đặt hàng với nhà cung cấp và thương hiệu do quản lý chọn. |
| /backoffice/purchase/ | The message for Supply · Send to Supply (was: The message for #supply · Send to #supply) | Tin nhắn gửi lên #supply · Gửi lên #supply | Tin nhắn gửi lên Supply · Gửi lên Supply |
| /backoffice/purchase/ | under the message: As Google Chat will show it. Change anything above and preview it again. (was: As Slack will show it. …) | Tin nhắn sẽ hiện trên Slack như thế này. Nếu sửa gì ở trên, hãy xem trước lại. | Tin nhắn sẽ hiện trên Google Chat như thế này. Nếu sửa gì ở trên, hãy xem trước lại. |
| /backoffice/purchase/ | Google Chat didn’t take it (what Google Chat said). Nothing you typed is lost: send it again. It won’t be posted twice. (was: Slack didn’t take it (what Slack said). …) | Slack chưa nhận yêu cầu (lỗi Slack báo). Những gì bạn nhập vẫn còn: hãy gửi lại. Yêu cầu sẽ không bị đăng hai lần. | Google Chat chưa nhận yêu cầu (lỗi Google Chat báo). Những gì bạn nhập vẫn còn: hãy gửi lại. Yêu cầu sẽ không bị đăng hai lần. |
| /backoffice/purchase/ | sent: Sent to Supply (was: Sent to #supply) | Đã gửi lên #supply | Đã gửi lên Supply |
| /backoffice/purchase/ | sent: Management will approve it in Google Chat and choose the supplier and brand. (was: … approve it in Slack and …) | Quản lý sẽ duyệt trên Slack rồi chọn nhà cung cấp và thương hiệu. | Quản lý sẽ duyệt trên Google Chat rồi chọn nhà cung cấp và thương hiệu. |
| /backoffice/purchase/ | a dry run: Dry run: not posted to Google Chat (was: … not posted to Slack) | Chạy thử: chưa đăng lên Slack | Chạy thử: chưa đăng lên Google Chat |
| /backoffice/purchases/ | lead: The last 30 purchase requests, newest first. Approving and ordering happen in Google Chat, so to know where a request is, ask management. (was: … happen in Slack, so …) | 30 yêu cầu mua hàng gần nhất, mới nhất ở trên. Việc duyệt và đặt hàng diễn ra trên Slack, nên muốn biết yêu cầu đã được xử lý đến đâu, hãy hỏi quản lý. | 30 yêu cầu mua hàng gần nhất, mới nhất ở trên. Việc duyệt và đặt hàng diễn ra trên Google Chat, nên muốn biết yêu cầu đã được xử lý đến đâu, hãy hỏi quản lý. |
| /backoffice/purchases/ | meta description: The last 30 purchase requests sent to Google Chat. (was: … sent to Slack.) | 30 yêu cầu mua hàng gần nhất đã gửi lên Slack. | 30 yêu cầu mua hàng gần nhất đã gửi lên Google Chat. |
| /backoffice/purchases/ | each request: Sent to Google Chat (was: Sent to Slack) | Đã gửi lên Slack | Đã gửi lên Google Chat |
| /backoffice/purchases/ | each request that wasn’t sent: Google Chat didn’t take it (what Google Chat said). (was: Slack didn’t take it (what Slack said).) | Slack chưa nhận yêu cầu (lỗi Slack báo). | Google Chat chưa nhận yêu cầu (lỗi Google Chat báo). |

What Google Chat said, inside the brackets, is in English on both pages, as Slack’s was: “Google Chat answered 404: NOT_FOUND”, say. Something new in the message itself, though no Vietnamese line: Google Chat has no way to show a typed < or > as plain text, so in a name, an item, a unit or a note they go as ‹ and ›, and a web address is opened up with a space (“https: //…”, “example. com”), so that nothing staff type can call someone or make a link. A few ordinary words change with it (“TP.HCM” goes as “TP. HCM”, “S.Pellegrino” as “S. Pellegrino”); a dot before one letter or a number stays (“D.O.P.”, “2.5 kg”, “1.250.000đ”).

Question for Linh (the four under 31 Oct and 29 Oct are still open):

5. **“không gian Supply”**: “không gian” is Google Chat’s own Vietnamese word for a space. Is that what the team will call it, or would “nhóm Supply”, or just “Supply”, read better? It’s in one line, the purchase request’s lead.

## Hiring round 2: jobs reopened, 8 Nov 2026

The jobs pages reopen: applications close on Saturday 14 November, and no start date is printed any more, only “Cuối tháng 11/2026”, with the exact date in the offer letter. The Restaurant Supervisor moves from “Vừa tuyển xong” to an open role, in Vietnamese for the first time, with its own address, careers@sol.pizza. Back on the site with their words unchanged, as they are whenever a round is open: “Cùng chúng tôi dựng nên Sol” and its lines on `/about/`, and “Chúng tôi sắp khai trương…” on `/jobs/`. Where a line changed, the old English is in brackets.

### The round

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| /jobs/ | each card’s dates: Applications close Sat 14 Nov · Start late November 2026 (was: Applications close Sun 4 Oct · Start Mon 12 Oct) | Hạn nộp: Chủ nhật 04/10 · Bắt đầu: thứ Hai 12/10 | Hạn nộp: thứ Bảy 14/11 · Bắt đầu: cuối tháng 11/2026 |
| /jobs/ | meta description: We’re hiring a Restaurant Supervisor and our opening team for the floor and the kitchen. Every application gets a reply. (was: We’re hiring a Host and our opening team …) | Chúng tôi đang tuyển Lễ tân (Host) và đội ngũ khai trương cho khu phục vụ và bếp. Mọi hồ sơ đều được phản hồi. | Chúng tôi đang tuyển Giám sát Nhà hàng và đội ngũ khai trương cho khu phục vụ và bếp. Mọi hồ sơ đều được phản hồi. |
| /jobs/ | meta description, once the round has closed: Work with Sol in Tây Hồ, Hanoi. Applications for our opening team closed on Saturday 14 November 2026. | Làm việc cùng Sol tại Tây Hồ, Hà Nội. Đợt tuyển đội ngũ khai trương đã đóng vào Chủ nhật 04/10/2026. | Làm việc cùng Sol tại Tây Hồ, Hà Nội. Đợt tuyển đội ngũ khai trương đã đóng vào thứ Bảy 14/11/2026. |
| /jobs/ | How to apply, after the jobs@sol.pizza sentence: For the Restaurant Supervisor, email careers@sol.pizza instead. | — | Riêng vị trí Giám sát Nhà hàng, vui lòng gửi tới careers@sol.pizza. |
| /jobs/ | a new group of cards, above Front of house: Leading the floor | — | Quản lý khu phục vụ |
| /jobs/ | the Supervisor’s card: Take full ownership of our dining room and bar: the floor, the team, the budget and the guest experience on every shift. | — | Chịu trách nhiệm toàn diện phòng ăn và quầy bar: khu phục vụ, đội ngũ, ngân sách và trải nghiệm của khách trong mọi ca. |
| /jobs/ | the Supervisor’s card, the Vietnamese title under the English one (English view only): Restaurant Supervisor | Giám sát nhà hàng (the Recently filled list) | Giám sát Nhà hàng |
| /jobs/ | the Supervisor’s card: Base salary 16,000,000–20,000,000 VND gross a month | — | Lương cơ bản 16.000.000 – 20.000.000 VNĐ gross/tháng |
| /jobs/ | the Supervisor’s card links, for screen readers only: Read the role: Restaurant Supervisor · Apply: Restaurant Supervisor | — | Xem mô tả công việc: Giám sát Nhà hàng (Restaurant Supervisor) · Ứng tuyển: Giám sát Nhà hàng (Restaurant Supervisor) |
| /jobs/, role pages | the closed note: Applications for this round closed on Saturday 14 November. Thank you to everyone who applied. | Đợt tuyển dụng này đã đóng vào Chủ nhật 04/10/2026. Cảm ơn tất cả các bạn đã ứng tuyển. | Đợt tuyển dụng này đã đóng vào thứ Bảy 14/11/2026. Cảm ơn tất cả các bạn đã ứng tuyển. |
| role pages | under the Apply buttons, at the top and the end: No email app? Send your CV to jobs@sol.pizza with the subject “Pizzaiolo — [Your name]”. (the role’s own address, and its name in English, as in the Apply email’s subject) | — | Không có ứng dụng email? Gửi CV tới jobs@sol.pizza với tiêu đề “Pizzaiolo — [Tên của bạn]”. |
| role pages | the button on that line, before and after a click: Copy address · Copied | — | Sao chép địa chỉ · Đã sao chép |
| role pages | meta description, the end: Applications close 14 November 2026. (was: … Sunday 4 October 2026.) | Hạn nộp 04/10/2026. | Hạn nộp 14/11/2026. |
| role pages | share card, the end (Vietnamese only) | Hạn nộp 04/10/2026. | Hạn nộp 14/11/2026. |
| the six descriptions | fact: Applications close · Saturday 14 November 2026 (was: Sunday 4 October 2026) | Hạn nộp hồ sơ · Chủ nhật 04/10/2026 | Hạn nộp hồ sơ · Thứ Bảy 14/11/2026 |
| the six descriptions | fact: Start · Late November 2026 — the exact date is in your offer letter (was: Monday 12 October 2026, or by Monday 19 October at the latest) | Ngày bắt đầu · Thứ Hai 12/10/2026, muộn nhất thứ Hai 19/10/2026 | Ngày bắt đầu · Cuối tháng 11/2026 — ngày chính xác được ghi trong thư mời nhận việc |
| the six descriptions | Essential: Able to start in late November 2026. (was: Able to start by Monday 19 October 2026.) | Có thể bắt đầu muộn nhất từ thứ Hai, ngày 19 tháng 10 năm 2026. | Có thể bắt đầu đi làm từ cuối tháng 11/2026. |
| the six descriptions | How to apply, first paragraph: Applications close Saturday 14 November 2026. We expect you to start in late November 2026. The restaurant is finishing its fit-out, so the exact date will be in your offer letter. Please don’t hand in your notice at your current job until you have it. (was: Applications close Sunday 4 October 2026. Start Monday 12 October 2026, or as soon as your notice allows and by Monday 19 October at the latest.) | Hạn chót nhận hồ sơ: Chủ nhật, ngày 4 tháng 10 năm 2026. Ngày bắt đầu làm việc: thứ Hai, ngày 12 tháng 10 năm 2026 (hoặc sớm nhất có thể tùy thời hạn báo nghỉ việc tại nơi làm việc hiện tại, nhưng muộn nhất là thứ Hai, ngày 19 tháng 10). | Hạn chót nhận hồ sơ: thứ Bảy, ngày 14 tháng 11 năm 2026. Dự kiến bạn sẽ bắt đầu đi làm từ cuối tháng 11/2026. Nhà hàng đang hoàn thiện những hạng mục cuối, nên ngày bắt đầu chính xác sẽ được ghi trong thư mời nhận việc. Bạn chưa nên xin nghỉ ở nơi làm việc hiện tại cho đến khi nhận được thư mời. |
| /jobs/pizzaiolo/ | The role in short: … under the Head Chef and the Sous Chef, who owns the dough programme. (was: … and, from 22 October, the Sous Chef, …) | … dưới sự điều hành của Bếp trưởng và, từ ngày 22/10, Bếp phó — người phụ trách chương trình bột. | … dưới sự điều hành của Bếp trưởng và Bếp phó — người phụ trách chương trình bột. |
| /jobs/line-cook/ | The role in short: … under the Head Chef and the Sous Chef. (was: … and, from 22 October, the Sous Chef.) | … dưới sự điều hành của Bếp trưởng và, từ ngày 22/10, Bếp phó. | … dưới sự điều hành của Bếp trưởng và Bếp phó. |

### The Restaurant Supervisor’s page

Its page lines, then the description line by line (`build/jobs/restaurant-supervisor.md`). The job description is new in Vietnamese: until now the page was in English, with a line saying so.

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| /jobs/restaurant-supervisor/ | page title: Restaurant Supervisor — Sol, Tây Hồ | Giám sát nhà hàng — Sol, Tây Hồ | Giám sát Nhà hàng (Restaurant Supervisor) — Sol, Tây Hồ |
| /jobs/restaurant-supervisor/ | meta description: Restaurant Supervisor at Sol, Tây Hồ, Hanoi. Base salary 16,000,000–20,000,000 VND a month, plus service charge and tips, est. 2,000,000–4,000,000 VND a month. Applications close 14 November 2026. (was: The Restaurant Supervisor role at Sol, Tây Hồ, Hanoi. This role has been filled.) | Mô tả công việc giám sát nhà hàng tại Sol, Tây Hồ, Hà Nội. Vị trí này đã tuyển xong. | Tuyển Giám sát Nhà hàng (Restaurant Supervisor) tại Sol, Tây Hồ, Hà Nội. Lương cơ bản 16–20 triệu + phí phục vụ ước tính 2–4 triệu/tháng. Hạn nộp 14/11/2026. |
| /jobs/restaurant-supervisor/ | share card (Vietnamese only) | — | Tuyển Restaurant Supervisor — Sol, Tây Hồ · Lương cơ bản 16–20 triệu + phí phục vụ ước tính 2–4 triệu/tháng. Hạn nộp 14/11/2026. |
| /jobs/restaurant-supervisor/ | the fact the build adds: Typical monthly total · 18,000,000 – 24,000,000 VND | — | Tổng thu nhập hằng tháng (ước tính) · 18.000.000 – 24.000.000 VNĐ |
| /jobs/restaurant-supervisor/ | the Apply email’s question: A short note (100 words is plenty) on the best service you have ever led or received, and why. | — | Một đoạn ngắn (khoảng 100 từ) về ca phục vụ tốt nhất bạn từng dẫn dắt hoặc từng trải nghiệm, và vì sao. |
| /jobs/restaurant-supervisor/ | title: Restaurant Supervisor | — | Giám sát Nhà hàng (Restaurant Supervisor) |
| /jobs/restaurant-supervisor/ | Front of House · Full-time · Tây Hồ, Hanoi | — | Bộ phận phục vụ · Toàn thời gian · Tây Hồ, Hà Nội |
| /jobs/restaurant-supervisor/ | fact: Reports to · General Director | — | Báo cáo cho · Giám đốc điều hành |
| /jobs/restaurant-supervisor/ | fact: Base salary · 16,000,000 – 20,000,000 VND gross per month, set on experience | — | Lương cơ bản · 16.000.000 – 20.000.000 VNĐ gross/tháng, tùy kinh nghiệm |
| /jobs/restaurant-supervisor/ | fact: Hours · Six shifts a week, 48 hours maximum, one rostered day off | — | Giờ làm · Sáu ca mỗi tuần, tối đa 48 giờ, một ngày nghỉ theo lịch |
| /jobs/restaurant-supervisor/ | fact: Applications close · Saturday 14 November 2026 | — | Hạn nộp hồ sơ · Thứ Bảy 14/11/2026 |
| /jobs/restaurant-supervisor/ | fact: Start · Late November 2026 — the exact date is in your offer letter | — | Ngày bắt đầu · Cuối tháng 11/2026 — ngày chính xác được ghi trong thư mời nhận việc |
| /jobs/restaurant-supervisor/ | **Take full ownership of our dining room and bar — the floor, the team, the departmental budget and the guest experience on every shift.** | — | **Chịu trách nhiệm toàn diện phòng ăn và quầy bar — khu phục vụ, đội ngũ, ngân sách của bộ phận và trải nghiệm của khách trong mọi ca.** |
| /jobs/restaurant-supervisor/ | heading: The role in short | — | Tóm tắt vị trí |
| /jobs/restaurant-supervisor/ | You report directly to the General Director and work in close partnership with the Head Chef. You lead the floor every service and carry real commercial responsibility for it. Joining now means building the service standard for our new space from the ground up. | — | Bạn báo cáo trực tiếp cho Giám đốc điều hành và phối hợp chặt chẽ với Bếp trưởng. Bạn dẫn dắt khu phục vụ trong mọi ca và thực sự chịu trách nhiệm về kết quả kinh doanh của khu vực này. Gia nhập vào thời điểm này nghĩa là bạn xây dựng tiêu chuẩn phục vụ cho không gian mới của chúng tôi ngay từ đầu. |
| /jobs/restaurant-supervisor/ | **Lead every service.** Table pacing, reservation flow and guest experience, with a strong floor presence at peak. | — | **Dẫn dắt mọi ca phục vụ.** Nhịp độ phục vụ tại bàn, luồng khách đặt bàn và trải nghiệm của khách, luôn có mặt trên sàn phục vụ vào giờ cao điểm. |
| /jobs/restaurant-supervisor/ | **Run the room.** Senior manager on duty, open and close, banking, and private events. | — | **Điều hành nhà hàng.** Là quản lý cấp cao nhất trong ca, mở và đóng cửa, nộp tiền ngân hàng và phụ trách các tiệc riêng. |
| /jobs/restaurant-supervisor/ | **Own the numbers.** Rosters and labour cost against the monthly target, daily POS closeouts, and front-of-house stock. | — | **Chịu trách nhiệm về các con số.** Lịch làm việc và chi phí nhân sự theo mục tiêu hằng tháng, chốt POS hằng ngày và hàng hóa của bộ phận phục vụ. |
| /jobs/restaurant-supervisor/ | **Build the team.** Hire, onboard, write the SOPs, coach, and run quarterly reviews. | — | **Xây dựng đội ngũ.** Tuyển dụng, hướng dẫn nhân viên mới, viết SOP, kèm cặp và đánh giá định kỳ hằng quý. |
| /jobs/restaurant-supervisor/ | **After 12 months we sponsor WSET Level 3 or the Certified Sommelier exam**, in exchange for a 2-year commitment. | — | **Sau 12 tháng, chúng tôi tài trợ khóa WSET Level 3 hoặc kỳ thi Certified Sommelier**, kèm cam kết làm việc 2 năm. |
| /jobs/restaurant-supervisor/ | heading: Responsibilities | — | Trách nhiệm cụ thể |
| /jobs/restaurant-supervisor/ | heading: Floor operations & shift leadership | — | Vận hành khu phục vụ và dẫn dắt ca |
| /jobs/restaurant-supervisor/ | Lead daily service, managing table pacing, reservation flow and guest experience end to end. | — | Dẫn dắt ca phục vụ hằng ngày, quản lý nhịp độ phục vụ tại bàn, luồng khách đặt bàn và trải nghiệm của khách từ đầu đến cuối. |
| /jobs/restaurant-supervisor/ | Run pre-shift briefings covering menu changes, specials, beverage pairings and shift targets. | — | Tổ chức họp đầu ca về các thay đổi trong thực đơn, món đặc biệt, gợi ý kết hợp đồ uống và mục tiêu của ca. |
| /jobs/restaurant-supervisor/ | Manage seating, section assignments and guest flow using our POS and ResDiary. | — | Quản lý việc sắp xếp chỗ ngồi, phân công khu vực và luồng khách bằng hệ thống POS và ResDiary của nhà hàng. |
| /jobs/restaurant-supervisor/ | Maintain a strong floor presence at peak, hosting, touching tables and supporting the bar. | — | Luôn có mặt trên sàn phục vụ vào giờ cao điểm: đón tiếp khách, ghé thăm các bàn và hỗ trợ quầy bar. |
| /jobs/restaurant-supervisor/ | heading: Venue & duty management | — | Quản lý nhà hàng và trực ca |
| /jobs/restaurant-supervisor/ | Act as the senior manager on duty in the General Director’s absence. | — | Là quản lý cấp cao nhất trong ca khi Giám đốc điều hành vắng mặt. |
| /jobs/restaurant-supervisor/ | Open and close the venue: keys, alarms, cash office, float preparation and end-of-night banking. | — | Mở và đóng cửa nhà hàng: chìa khóa, báo động, phòng giữ tiền, chuẩn bị tiền lẻ đầu ca và nộp tiền cuối ngày. |
| /jobs/restaurant-supervisor/ | Handle incidents and emergencies — guest injury, staff conflict, security, fire and first aid — and report every one. | — | Xử lý sự cố và tình huống khẩn cấp — khách bị thương, mâu thuẫn giữa nhân viên, an ninh, hỏa hoạn và sơ cứu — và báo cáo mọi trường hợp. |
| /jobs/restaurant-supervisor/ | Coordinate reservations, private events and large bookings end to end. | — | Điều phối đặt bàn, tiệc riêng và các đặt bàn nhóm đông từ đầu đến cuối. |
| /jobs/restaurant-supervisor/ | heading: Rostering, cost control & reporting | — | Xếp lịch, kiểm soát chi phí và báo cáo |
| /jobs/restaurant-supervisor/ | Build and manage weekly rosters against sales forecasts, holding FOH labour cost against the monthly target. | — | Lập và quản lý lịch làm việc hằng tuần theo dự báo doanh thu, giữ chi phí nhân sự của bộ phận phục vụ theo mục tiêu hằng tháng. |
| /jobs/restaurant-supervisor/ | Perform POS closeouts, till reconciliation, and discount, void and comp audits; submit end-of-day revenue reports. | — | Thực hiện chốt POS, đối soát két tiền, kiểm tra các khoản giảm giá, hủy món và miễn phí; nộp báo cáo doanh thu cuối ngày. |
| /jobs/restaurant-supervisor/ | Manage front-of-house stock only — beverages, glassware, smallwares and operating supplies — and track breakage and waste. Kitchen ingredients are ordered by the kitchen. | — | Chỉ quản lý hàng hóa của bộ phận phục vụ — đồ uống, ly tách, dụng cụ nhỏ và vật tư vận hành — và theo dõi đổ vỡ, hao hụt. Nguyên liệu bếp do bộ phận bếp đặt. |
| /jobs/restaurant-supervisor/ | Contribute to the monthly FOH budget and report departmental performance against it. | — | Tham gia xây dựng ngân sách hằng tháng của bộ phận phục vụ và báo cáo kết quả so với ngân sách đó. |
| /jobs/restaurant-supervisor/ | heading: Kitchen partnership | — | Phối hợp với bếp |
| /jobs/restaurant-supervisor/ | Coordinate with the Head Chef on ticket times, pass management and dining room pacing. | — | Phối hợp với Bếp trưởng về thời gian ra món, điều phối khu pass và nhịp độ phục vụ trong phòng ăn. |
| /jobs/restaurant-supervisor/ | Train the FOH team on dishes, sourcing, dietary restrictions and allergen handling. | — | Đào tạo đội ngũ phục vụ về món ăn, nguồn nguyên liệu, các chế độ ăn kiêng và cách xử lý thông tin dị ứng. |
| /jobs/restaurant-supervisor/ | Feed real-time guest feedback back to the kitchen. | — | Chuyển ngay phản hồi của khách cho bếp. |
| /jobs/restaurant-supervisor/ | heading: Hiring, training & standards | — | Tuyển dụng, đào tạo và tiêu chuẩn |
| /jobs/restaurant-supervisor/ | Interview, hire and onboard FOH team members with the General Director. | — | Cùng Giám đốc điều hành phỏng vấn, tuyển dụng và hướng dẫn nhân viên phục vụ mới. |
| /jobs/restaurant-supervisor/ | Write, document and enforce SOPs for greeting, sequence of service, beverage presentation and upselling. | — | Viết, lưu trữ và đảm bảo thực hiện các SOP về chào đón khách, trình tự phục vụ, cách phục vụ đồ uống và gợi ý bán thêm. |
| /jobs/restaurant-supervisor/ | Coach continuously, run quarterly performance reviews, and manage underperformance fairly and on the record. | — | Kèm cặp thường xuyên, đánh giá hiệu suất hằng quý, và xử lý các trường hợp chưa đạt yêu cầu một cách công bằng, có ghi nhận bằng văn bản. |
| /jobs/restaurant-supervisor/ | heading: Guest relations & reputation | — | Quan hệ với khách và uy tín của nhà hàng |
| /jobs/restaurant-supervisor/ | Act as the escalation point for guest complaints and service recovery. | — | Là đầu mối tiếp nhận khiếu nại của khách và khắc phục sự cố dịch vụ. |
| /jobs/restaurant-supervisor/ | Monitor and respond to Google, TripAdvisor and social reviews. | — | Theo dõi và phản hồi các đánh giá trên Google, TripAdvisor và mạng xã hội. |
| /jobs/restaurant-supervisor/ | Support marketing on the floor — promotions, content capture and guest follow-up. | — | Hỗ trợ marketing ngay tại nhà hàng — chương trình khuyến mãi, ghi hình nội dung và chăm sóc khách sau bữa ăn. |
| /jobs/restaurant-supervisor/ | Ensure compliance with food safety standards and responsible alcohol service. | — | Đảm bảo tuân thủ tiêu chuẩn an toàn thực phẩm và phục vụ rượu bia có trách nhiệm. |
| /jobs/restaurant-supervisor/ | heading: First 90 days | — | 90 ngày đầu tiên |
| /jobs/restaurant-supervisor/ | **Days 1–30.** Learn the menu, wine and cocktail list to service standard. Work every FOH position. | — | **Ngày 1–30.** Nắm vững thực đơn, danh sách vang và cocktail theo tiêu chuẩn phục vụ. Làm qua mọi vị trí của bộ phận phục vụ. |
| /jobs/restaurant-supervisor/ | **Days 31–60.** Own the roster, the daily closeout and the open/close routine. Document the sequence of service. | — | **Ngày 31–60.** Phụ trách lịch làm việc, việc chốt sổ hằng ngày và quy trình mở, đóng cửa. Viết thành văn bản trình tự phục vụ. |
| /jobs/restaurant-supervisor/ | **Days 61–90.** Hold labour cost against the monthly target for a full month and have a written FOH SOP pack in use. | — | **Ngày 61–90.** Giữ chi phí nhân sự theo mục tiêu hằng tháng trong trọn một tháng và đưa bộ SOP bằng văn bản của bộ phận phục vụ vào sử dụng. |
| /jobs/restaurant-supervisor/ | heading: How we measure | — | Tiêu chí đánh giá |
| /jobs/restaurant-supervisor/ | FOH labour cost against the monthly target | — | Chi phí nhân sự của bộ phận phục vụ so với mục tiêu hằng tháng |
| /jobs/restaurant-supervisor/ | Average spend per guest and beverage attachment rate | — | Mức chi tiêu trung bình mỗi khách và tỷ lệ khách gọi kèm đồ uống |
| /jobs/restaurant-supervisor/ | Google and TripAdvisor rating and review volume | — | Điểm đánh giá và số lượng đánh giá trên Google và TripAdvisor |
| /jobs/restaurant-supervisor/ | Covers per service and table turn time | — | Số khách mỗi ca và thời gian xoay vòng bàn |
| /jobs/restaurant-supervisor/ | FOH team retention and training completion | — | Tỷ lệ giữ chân nhân viên bộ phận phục vụ và mức độ hoàn thành đào tạo |
| /jobs/restaurant-supervisor/ | Stock variance on beverage and breakage | — | Chênh lệch tồn kho đồ uống và tỷ lệ đổ vỡ |
| /jobs/restaurant-supervisor/ | heading: Essential | — | Yêu cầu bắt buộc |
| /jobs/restaurant-supervisor/ | 3+ years of progressive front-of-house leadership (Supervisor, Floor Captain, Assistant Manager or Shift Lead) in a high-volume restaurant, wine bar or casual fine-dining venue. | — | Có từ 3 năm kinh nghiệm trở lên ở các vị trí quản lý tiền sảnh với trách nhiệm tăng dần (Giám sát, Floor Captain, Trợ lý Quản lý hoặc Trưởng ca) tại nhà hàng đông khách, wine bar hoặc nhà hàng casual fine-dining. |
| /jobs/restaurant-supervisor/ | Proven commercial experience: rostering, labour cost control, inventory and shift reconciliation. | — | Có kinh nghiệm thực tế về mặt kinh doanh: xếp lịch làm việc, kiểm soát chi phí nhân sự, quản lý hàng tồn kho và đối soát ca. |
| /jobs/restaurant-supervisor/ | Comfortable being the most senior person in the building — able to make decisions, handle incidents and close the venue. | — | Tự tin khi là người phụ trách cao nhất tại nhà hàng — có thể tự ra quyết định, xử lý sự cố và đóng cửa nhà hàng. |
| /jobs/restaurant-supervisor/ | Fluent Vietnamese and professional working English — comfortable hosting international guests. | — | Thành thạo tiếng Việt và sử dụng tốt tiếng Anh trong công việc — tự tin tiếp đón khách quốc tế. |
| /jobs/restaurant-supervisor/ | Confident with POS and reservation systems, and with Excel or Google Sheets. | — | Sử dụng thành thạo hệ thống POS và hệ thống đặt bàn, cùng Excel hoặc Google Sheets. |
| /jobs/restaurant-supervisor/ | Available for split shifts, evenings, weekends and public holidays, including Tết trading. | — | Sẵn sàng làm ca gãy, buổi tối, cuối tuần và ngày lễ, bao gồm cả dịp Tết. |
| /jobs/restaurant-supervisor/ | heading: Nice to have | — | Ưu tiên |
| /jobs/restaurant-supervisor/ | Wine, cocktail or barista knowledge — WSET Level 2 or equivalent. | — | Có kiến thức về vang, cocktail hoặc pha chế cà phê — WSET Level 2 hoặc tương đương. |
| /jobs/restaurant-supervisor/ | Experience opening or relaunching a venue. | — | Có kinh nghiệm khai trương hoặc tái khởi động một nhà hàng. |
| /jobs/restaurant-supervisor/ | Experience managing a venue’s social media or review channels. | — | Có kinh nghiệm quản lý mạng xã hội hoặc các kênh đánh giá của nhà hàng. |
| /jobs/restaurant-supervisor/ | heading: Pay and benefits | — | Lương và phúc lợi |
| /jobs/restaurant-supervisor/ | heading: Pay | — | Mức lương |
| /jobs/restaurant-supervisor/ | **Base salary:** 16,000,000 – 20,000,000 VND gross per month, set on experience. | — | **Lương cơ bản:** 16.000.000 – 20.000.000 VNĐ gross/tháng, tùy kinh nghiệm. |
| /jobs/restaurant-supervisor/ | **Service charge & tips:** 2,000,000 – 4,000,000 VND per month from the venue’s 5% service charge and FOH tip pool, paid quarterly, starting once we open. | — | **Phí phục vụ & tip:** 2.000.000 – 4.000.000 VNĐ/tháng (từ 5% phí phục vụ của nhà hàng và quỹ tip của bộ phận phục vụ), chi trả theo quý, bắt đầu khi nhà hàng mở cửa. |
| /jobs/restaurant-supervisor/ | **Typical monthly total:** 18,000,000 – 24,000,000 VND once the estimated service charge share is included, before the quarterly bonus. | — | **Tổng thu nhập hằng tháng (ước tính):** 18.000.000 – 24.000.000 VNĐ (đã bao gồm phần phí phục vụ dự kiến, chưa gồm thưởng quý). |
| /jobs/restaurant-supervisor/ | **Performance bonus:** quarterly KPI bonus of up to 10% of quarterly base salary. | — | **Thưởng hiệu suất:** thưởng KPI theo quý, tối đa 10% lương quý. |
| /jobs/restaurant-supervisor/ | 13-month bonus according to company KPIs. | — | Thưởng tháng 13 dựa theo chỉ số KPI của công ty. |
| /jobs/restaurant-supervisor/ | Annual salary review based on performance. | — | Xét tăng lương hằng năm dựa trên hiệu suất làm việc. |
| /jobs/restaurant-supervisor/ | **Probation:** 30 days at 85% of base salary. | — | **Thử việc:** 30 ngày, hưởng 85% lương cơ bản. |
| /jobs/restaurant-supervisor/ | heading: Benefits | — | Phúc lợi |
| /jobs/restaurant-supervisor/ | Full employer contribution to compulsory Social, Health and Unemployment Insurance (BHXH, BHYT, BHTN) from the start of your labour contract. | — | Công ty đóng đầy đủ phần của người sử dụng lao động cho BHXH, BHYT, BHTN bắt buộc kể từ khi hợp đồng lao động bắt đầu. |
| /jobs/restaurant-supervisor/ | 12 days paid annual leave a year, plus 1 additional day per 3 years of service, subject to company policy. | — | 12 ngày phép năm có lương, cộng 1 ngày cho mỗi 3 năm làm việc (theo chính sách công ty). |
| /jobs/restaurant-supervisor/ | 11 paid public holidays a year including Tết. Holiday work is paid at statutory premium rates. | — | 11 ngày nghỉ lễ, Tết có hưởng lương trong năm. Làm việc vào ngày lễ được trả lương theo mức quy định của pháp luật. |
| /jobs/restaurant-supervisor/ | Overtime paid in accordance with Vietnamese labour law and company policy. | — | Lương làm thêm giờ được chi trả theo quy định của Bộ luật Lao động và chính sách công ty. |
| /jobs/restaurant-supervisor/ | A staff meal cooked by our kitchen before dinner service. | — | Bữa ăn nhân viên do bếp chuẩn bị trước giờ phục vụ bữa tối. |
| /jobs/restaurant-supervisor/ | Sol T-shirts and a branded half apron provided. Our dress code is black; the T-shirt is not required to start. | — | Được cấp áo phông Sol và tạp dề ngang (half-apron) có logo thương hiệu. Quy định trang phục là màu đen; không bắt buộc mặc áo phông Sol ngay khi mới bắt đầu. |
| /jobs/restaurant-supervisor/ | Staff dining discount across Sol and ASU House Bakery. | — | Giảm giá nhân viên khi dùng bữa tại Sol và ASU House Bakery. |
| /jobs/restaurant-supervisor/ | **Funded qualification:** after 12 months of service, Sol will sponsor WSET Level 3 or the Certified Sommelier examination, in exchange for a 2-year service commitment from the date of sponsorship. | — | **Tài trợ chứng chỉ:** sau 12 tháng làm việc, Sol tài trợ khóa WSET Level 3 hoặc kỳ thi Certified Sommelier, kèm cam kết làm việc 2 năm kể từ thời điểm được tài trợ. |
| /jobs/restaurant-supervisor/ | heading: Schedule | — | Lịch làm việc |
| /jobs/restaurant-supervisor/ | Six shifts a week, 48 hours maximum, one rostered day off. Split shifts, evenings, weekends and public holidays including Tết trading. | — | Sáu ca mỗi tuần, tối đa 48 giờ, một ngày nghỉ theo lịch phân công. Làm ca gãy (chia ca), buổi tối, cuối tuần và ngày lễ, bao gồm cả dịp Tết. |
| /jobs/restaurant-supervisor/ | heading: How to apply | — | Cách thức ứng tuyển |
| /jobs/restaurant-supervisor/ | Applications close Saturday 14 November 2026. We expect you to start in late November 2026. The restaurant is finishing its fit-out, so the exact date will be in your offer letter. Please don’t hand in your notice at your current job until you have it. | — | Hạn chót nhận hồ sơ: thứ Bảy, ngày 14 tháng 11 năm 2026. Dự kiến bạn sẽ bắt đầu đi làm từ cuối tháng 11/2026. Nhà hàng đang hoàn thiện những hạng mục cuối, nên ngày bắt đầu chính xác sẽ được ghi trong thư mời nhận việc. Bạn chưa nên xin nghỉ ở nơi làm việc hiện tại cho đến khi nhận được thư mời. |
| /jobs/restaurant-supervisor/ | Send to careers@sol.pizza with the subject line “Restaurant Supervisor — [Your name]”: | — | Vui lòng gửi hồ sơ đến careers@sol.pizza với tiêu đề “Restaurant Supervisor — [Tên của bạn]”, bao gồm: |
| /jobs/restaurant-supervisor/ | Your CV. | — | Sơ yếu lý lịch (CV) của bạn. |
| /jobs/restaurant-supervisor/ | A short note (100 words is plenty) on the best service you have ever led or received, and why. | — | Một đoạn ngắn (khoảng 100 từ) về ca phục vụ tốt nhất bạn từng dẫn dắt hoặc từng trải nghiệm, và vì sao. |
| /jobs/restaurant-supervisor/ | heading: Our process | — | Quy trình tuyển dụng |
| /jobs/restaurant-supervisor/ | Application review within 5 working days → 30-minute conversation → paid trial shift → offer. We reply to every applicant. | — | Xét duyệt hồ sơ trong vòng 5 ngày làm việc → Trao đổi 30 phút → Buổi làm thử (trial shift) có trả lương → Đưa ra đề nghị tuyển dụng. Chúng tôi phản hồi tất cả các ứng viên. |

No longer on the site:

- `/jobs/`: “Giám sát nhà hàng · Tháng 9 năm 2026” under “Vừa tuyển xong”.
- `/vi/jobs/restaurant-supervisor`: the old page, with “Vị trí này đã tuyển xong. Cảm ơn tất cả các bạn đã ứng tuyển.” and “Bản mô tả công việc này chỉ có bằng tiếng Anh.” Both lines stay on the two other filled roles. The address without the slash now leads to the new page.

Questions for Linh:

1. **“Giám đốc điều hành”** for General Director: the applicant privacy notice already calls that person this. Is it the title you want on the job description?
2. **“Quản lý khu phục vụ”**, the new group on `/jobs/`, sits right above “Bộ phận phục vụ”. Do the two read clearly next to each other?
3. **The words left in English** in the Supervisor’s description: POS, SOP, KPI, wine bar, casual fine-dining, Floor Captain, trial shift. Are they how the trade says it here?

## Online booking: the ResDiary widget, 4 Nov 2026

The booking form is on `/booking/` and `/vi/booking/`, in a frame from ResDiary. There’s one widget, in English, so the form itself stays in English on the Vietnamese page for now; its words are ResDiary’s, not in this file. The lines marked “(once online booking is live)” in the 13 Oct sections below are live now too: the phone bar’s Gọi, “Không đặt được qua biểu mẫu?” under the form, and the page’s description. The opening-week form (Giữ bàn cho tôi trong tuần khai trương) comes off `/booking/`. These are the lines that weren’t in this file yet. Where a line changed, the old English is in brackets.

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| /booking/ | lead: Book online below, or call or email us. (was: Online booking opens closer to the day we open. Until then, call or email us and we’ll hold you a table for opening week.) | Chúng tôi sẽ mở đặt bàn trực tuyến khi gần đến ngày khai trương. Từ nay đến lúc đó, bạn cứ gọi điện hoặc gửi email, chúng tôi sẽ giữ bàn cho bạn trong tuần khai trương. | Đặt bàn trực tuyến ngay bên dưới, hoặc gọi điện hay gửi email cho chúng tôi. |
| /booking/ | the form’s frame, its title for screen readers: Book a table at Sol | — | Đặt bàn tại Sol |
| /accessibility/ | full previews only, under Booking: The booking form comes from ResDiary, inside our page. If it gives you any trouble, call us on +84 866 161 600 or write to hello@sol.pizza, and we’ll book for you. (was: To book, call us on +84 866 161 600 or write to hello@sol.pizza, and we’ll look after the rest.) | Để đặt bàn, hãy gọi +84 866 161 600 hoặc viết cho chúng tôi qua hello@sol.pizza, chúng tôi sẽ lo phần còn lại. | Biểu mẫu đặt bàn là của ResDiary, nằm trong trang của chúng tôi. Nếu bạn gặp khó khăn, hãy gọi +84 866 161 600 hoặc viết cho chúng tôi qua hello@sol.pizza, chúng tôi sẽ đặt bàn giúp bạn. |

## The site password: the sign-in page, 6 Nov 2026

A new page at `/login/` and `/vi/login/`, seen only while the site password is on: everyone without the password lands there, from every page but careers. Every line is new, though the two warnings are the back office’s and the button is the footer’s.

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| /login/ | page title: Sign in — Sol | — | Đăng nhập — Sol |
| /login/ | meta description: Our new site is still being finished. Our careers pages are open to everyone. | — | Trang web mới của chúng tôi vẫn đang được hoàn thiện. Các trang tuyển dụng mở cho tất cả mọi người. |
| /login/ | heading: We’re still working on this site. | — | Chúng tôi vẫn đang hoàn thiện trang web này. |
| /login/ | Until it’s ready, it’s open only to people with the password. | — | Trong thời gian này, trang chỉ mở cho những người có mật khẩu. |
| /login/ | the form: Password · Enter | — | Mật khẩu · Vào trang |
| /login/ | a wrong password: That isn’t the password. Try again. | — | Mật khẩu chưa đúng. Hãy thử lại. |
| /login/ | too many tries: Too many tries. Wait 15 minutes, then try again. | — | Bạn đã thử quá nhiều lần. Hãy đợi 15 phút rồi thử lại. |
| /login/ | You stay signed in on this device for 30 days. | — | Bạn sẽ được giữ đăng nhập trên thiết bị này trong 30 ngày. |
| /login/ | Looking for a job at Sol? Our careers pages are open to everyone. | — | Bạn đang tìm việc tại Sol? Các trang tuyển dụng của chúng tôi mở cho tất cả mọi người. |
| /login/ | the button: Work with us | — | Tuyển dụng |

## The back office: item requests, 31 Oct 2026

Staff now ask for items only: the purchase request has no supplier, brand, price or estimate any more, as management chooses the supplier and the brand when they order. These are the back office’s new and changed lines. The 29 Oct section below keeps the lines that stay as they were; the ones that went (the supplier, the Order Guide, prices, the estimate, Arman’s ✅) are gone from it. Since 12 Nov the requests go to Google Chat (the section at the top): the lines that said Slack or #supply are there now, with what they said before. Where a line changed, the old English is in brackets.

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| /backoffice/purchase/ | under Items: Write what you need, not the brand or the supplier: management chooses those when they order. Use the note for size, ripeness or what it’s for. (was: Pick from the supplier’s list, in English or Vietnamese, or type an item that isn’t on it: it goes without a price.) | Chọn từ danh sách của nhà cung cấp, bằng tiếng Anh hoặc tiếng Việt, hoặc tự nhập mặt hàng chưa có trong danh sách: mặt hàng đó sẽ không có giá. | Ghi mặt hàng cần mua, không cần ghi thương hiệu hay nhà cung cấp: quản lý sẽ chọn khi đặt hàng. Dùng ô ghi chú cho kích cỡ, độ chín hoặc món sẽ dùng. |
| /backoffice/purchase/ | each item, the units: Choose… · kg · g · L · ml · pc · pack · box · bottle · can · jar · bag · sack · bunch · tray · case · roll · Other… | — | Chọn… · kg · g · L · ml · cái · gói · hộp · chai · lon · hũ · túi · bao · bó · khay · thùng · cuộn · Khác… |
| /backoffice/purchase/ | each item: Other unit (the box Other… opens) · in the item’s note until something is typed: Size, ripeness, what it’s for | — | Đơn vị khác · Kích cỡ, độ chín, dùng cho món gì |
| /backoffice/purchase/ | in the message on the page, where Google Chat will show the approver’s name: @Kitchen approver · @Bar & FOH approver | — | @người duyệt của Bếp · @người duyệt của Bar và Sảnh |
| /backoffice/purchases/ | each request: Not sent (was: Not sent: Slack failed) | Chưa gửi: lỗi Slack | Chưa gửi |
| /backoffice/purchases/ | each request, its items, with the units as on the form: Basil — 4 bunch (big leaves) | — | Basil — 4 bó (big leaves) |
| Supply | the message in Google Chat, each line in both languages: 📝 YÊU CẦU MUA HÀNG / PURCHASE REQUEST · Bộ phận / Station · Cần lúc / Needed by · Hàng / Items · Người yêu cầu / Requested by · Ghi chú / Note · Duyệt / Approve · Đặt hàng / Ordering: quản lý chọn NCC và thương hiệu / management picks the supplier and brand · Gửi từ sol.pizza/backoffice · Ref; a unit as 4 bó/bunch | — | YÊU CẦU MUA HÀNG · Bộ phận · Cần lúc · Hàng · Người yêu cầu · Ghi chú · Duyệt · Đặt hàng: quản lý chọn NCC và thương hiệu · Gửi từ sol.pizza/backoffice |

The message’s lines are the brief’s, and never change once it’s live: an agent may read Supply by them. If one reads wrong, say so before it goes live.

Questions for Linh (the three under 29 Oct are still open):

4. **The units**: cái, gói, hộp, chai, lon, hũ, túi, bao, bó, khay, thùng, cuộn, and Khác… for Other. Are they the words the kitchen and the bar use (thùng for a case, khay for a tray, bao for a sack)? They show on the form, on Recent requests and in the message in Supply (as thùng/case), so they’re best settled before the team starts.

## The back office: purchase requests, 29 Oct 2026

New pages for the team, behind the staff password and out of search: the back office’s home (`/backoffice/`), its sign-in page, the purchase request (`/backoffice/purchase/`) and the recent requests (`/backoffice/purchases/`). Every line was new. Since 31 Oct staff ask for items only (the section above): the lines that went with the supplier, the Order Guide, prices and the estimate are gone, from the pages and from this table, and the lines that changed are above, with what they said before. Since 12 Nov the requests go to Google Chat: the lines that said Slack or #supply are in the section at the top. Numbers follow the language, as in the kitchen (2.5 in English, 2,5 in Vietnamese). Items and people’s names show as staff type them.

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| /backoffice/ | eyebrow: Staff only · heading and page title: Back office; Back office — Sol | — | Dành cho nhân viên · Nội bộ; Nội bộ — Sol |
| /backoffice/ | lead: Sol’s tools for the team. · meta description: Sol’s back office: tools for the team. | — | Công cụ của Sol dành cho nhân viên. · Trang nội bộ của Sol: công cụ cho nhân viên. |
| all four | menu: Back office · Purchase request · Recent requests · Sign out | — | Nội bộ · Yêu cầu mua hàng · Yêu cầu gần đây · Đăng xuất |
| /backoffice/ | Dough (kitchen) · The dough calculator and the dough log. They have their own password. | — | Bột (bếp) · Công cụ tính bột và nhật ký bột. Có mật khẩu riêng. |
| /backoffice/login/ | eyebrow on the other back-office pages: Back office · page title: Sign in — Sol back office | — | Nội bộ · Đăng nhập — Nội bộ Sol |
| /backoffice/login/ | The back office is for Sol’s team. Ask a manager for the staff password. · meta description: Sign in to Sol’s back office. | — | Trang nội bộ dành cho nhân viên Sol. Hãy hỏi quản lý để biết mật khẩu nhân viên. · Đăng nhập vào trang nội bộ của Sol. |
| /backoffice/login/ | Staff password (the other lines as the kitchen’s sign-in page) | — | Mật khẩu nhân viên |
| /backoffice/purchase/ | heading and page title: Purchase request; Purchase request — Sol | — | Yêu cầu mua hàng; Yêu cầu mua hàng — Sol |
| /backoffice/purchase/ | without JavaScript: The form needs JavaScript. Turn it on in the browser’s settings. | — | Biểu mẫu này cần JavaScript. Hãy bật JavaScript trong cài đặt trình duyệt. |
| /backoffice/purchase/ | The back office isn’t set up on this copy of the site. | — | Trang nội bộ chưa được thiết lập trên bản này của trang. |
| /backoffice/purchase/ | The request · Requested by | — | Yêu cầu · Người yêu cầu |
| /backoffice/purchase/ | Station: Kitchen · Bar · FOH | — | Bộ phận: Bếp · Bar · Sảnh |
| /backoffice/purchase/ | Needed by · Day · Time (optional) | — | Cần lúc · Ngày · Giờ (không bắt buộc) |
| /backoffice/purchase/ | Items | — | Hàng |
| /backoffice/purchase/ | each item: Item 1 · Remove (for screen readers: Remove item 1) · Item · Quantity · Unit · Note (optional) | — | Hàng 1 · Xóa (Xóa hàng 1) · Hàng · Số lượng · Đơn vị · Ghi chú (không bắt buộc) |
| /backoffice/purchase/ | Add an item · 30 items at most. Send the rest as another request. · Note | — | Thêm hàng · Tối đa 30 mặt hàng. Hãy gửi phần còn lại trong một yêu cầu khác. · Ghi chú |
| /backoffice/purchase/ | Preview the message | — | Xem trước tin nhắn |
| /backoffice/purchase/ | Check the marked boxes. · Writing the message… · Sending… | — | Kiểm tra lại các ô được đánh dấu. · Đang soạn tin nhắn… · Đang gửi… |
| /backoffice/purchase/ | It’s still being sent. Wait a moment, then send it again: it won’t be posted twice. | — | Yêu cầu vẫn đang được gửi. Hãy đợi một chút rồi gửi lại: yêu cầu sẽ không bị đăng hai lần. |
| /backoffice/purchase/ | Couldn’t send it. Check the connection and try again: it won’t be posted twice. | — | Chưa gửi được. Hãy kiểm tra kết nối và thử lại: yêu cầu sẽ không bị đăng hai lần. |
| /backoffice/purchase/ | You’ve been signed out. Sign in in a new tab, then send it again here. | — | Bạn đã bị đăng xuất. Hãy đăng nhập ở một thẻ mới, rồi gửi lại ở đây. |
| /backoffice/purchase/ | sent: Ref REQ-261105-2143 · New request | — | Mã REQ-261105-2143 · Yêu cầu mới |
| /backoffice/purchase/ | a dry run: This copy of the site only pretends to post. The message it would have posted: | — | Bản này của trang chỉ chạy thử, không đăng thật. Tin nhắn lẽ ra sẽ được đăng: |
| /backoffice/purchases/ | heading and page title: Recent requests; Recent requests — Sol | — | Yêu cầu gần đây; Yêu cầu gần đây — Sol |
| /backoffice/purchases/ | The list needs JavaScript. … · Loading… · No requests yet. Send one from the purchase request. | — | Danh sách cần JavaScript. … · Đang tải… · Chưa có yêu cầu nào. Hãy gửi một yêu cầu từ trang yêu cầu mua hàng. |
| /backoffice/purchases/ | Couldn’t load the list. Check the connection and reload the page. · You’ve been signed out. Sign in again. | — | Không tải được danh sách. Hãy kiểm tra kết nối và tải lại trang. · Bạn đã bị đăng xuất. Đăng nhập lại. |
| /backoffice/purchases/ | each request: Dry run · Sending | — | Chạy thử · Đang gửi |
| /backoffice/purchases/ | each request: Station · Needed by · Items | — | Bộ phận · Cần lúc · Hàng |

Questions for Linh:

1. **“Nội bộ”** for Back office (the eyebrow, the menu and the page titles): clear to the team, or would “Văn phòng” or “Quản lý” read better?
2. **“Sảnh”** for FOH (front of house): the word the team uses? (“Danh mục hàng”, the Order Guide’s name, went with it on 31 Oct.)
3. **“Xóa”** on the purchase request (as asked for), while the dough log says “Xoá”: keep both, or make them the same?

## Search: structured data, 13 Oct 2026

Nothing new to read on the pages. What search engines read changes: the restaurant's details, the menus, the Eclipse editions and each page's breadcrumb now come in the page's language. The Vietnamese is the site's own: the address as on the pages (Số 7, Ngõ 88 Quảng An, Tây Hồ, Hà Nội), the home page's description, the menus' section names and descriptions, the page titles (for the breadcrumbs), and each Eclipse edition's own summary once it has one. The menus' names in it: Sol: Món ăn · Sol: Vang · Sol: Quầy bar; a wine's two prices: ly · chai. How guests pay, once it's set, comes from the Vietnamese half of `PAYMENT_ACCEPTED` in `build/gen.py`, which also answers “Thanh toán” on /vi/visit-us/: please read it then.

## Photographs, 13 Oct 2026

The photos come with their own alt text, in English and Vietnamese, written in `build/media.json` as each one is added: please read each photo's `alt_vi` when it arrives. The site's own new lines:

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| /press/ | Photographs · Photo: (the photographer) · Full size | — | Hình ảnh · Ảnh: (tên nhiếp ảnh gia) · Ảnh gốc |
| /press/ | each Full size link, for screen readers: Full size: (the photo's alt text) | — | Ảnh gốc: (alt_vi của ảnh) |
| every page with a gallery | its label for screen readers: Photographs | — | Hình ảnh |
| full previews only | a photo still to come: Photo `slot`: what to shoot (2:1 wide, 4:5 on a phone, up to 3) | — | Ảnh `slot`: … (2:1 trên màn hình rộng, 4:5 trên điện thoại, tối đa 3 ảnh) |

## The home page, events, press and the pages to come, 13 Oct 2026

The home page in a new order, Events (Eclipse), Press, and pages built ahead of their content. Lines marked “(full previews only)” wait for content or for the lawyer, and aren't on sol.pizza until then; “(once open)” and “(once priced)” appear from opening day, or once the menu has its prices.

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| / | eyebrow: Italian-American · Tây Hồ, Hanoi (the opening date moves under the buttons) | Sắp khai trương · Tây Hồ, Hà Nội | Ẩm thực Ý–Mỹ · Tây Hồ, Hà Nội |
| / | under the buttons: Opening soon; (with a date) Opening Thursday 5 November; (once open) Open today, 5pm–11pm · Closed today · Tuesday to Sunday, 5pm–11pm | — | Sắp khai trương; Khai trương thứ Năm 05/11; Hôm nay mở cửa 17:00 – 23:00 · Hôm nay nghỉ · Thứ Ba đến Chủ Nhật, 17:00 – 23:00 |
| / | three ways in: Menu · Pizza from the wood oven, pasta made in-house and 26 wines by the glass. · See the menu | — | Thực đơn · Pizza từ lò củi, mì Ý làm tại nhà hàng và 26 loại vang theo ly. · Xem thực đơn |
| / | Private dining · Seven or more, or a night that’s all yours. · Tell us about it | — | Tiệc riêng · Từ bảy người trở lên, hay một buổi tối chỉ dành riêng cho bạn. · Cho chúng tôi biết |
| / | Events · Eclipse is Sol’s pop-up series. · See what’s on (and, if a page is taken down, Visit · No 7, Lane 88 Quang An, Tây Hồ: how to find us. · Find us) | — | Sự kiện · Eclipse là chuỗi sự kiện pop-up của Sol. · Xem lịch sự kiện (Ghé thăm · Số 7, ngõ 88 Quảng An, Tây Hồ: đường đến Sol. · Tìm chúng tôi) |
| / | the story: Our story · We closed Sol Pizza to build Sol. · (the lead, moved from the top) · Read our story | (as on About) | (as on About) · Đọc câu chuyện của chúng tôi |
| / | the next Eclipse: Eclipse · First edition · Friday 23 and Saturday 24 October 2026 · Eclipse is Sol’s pop-up series. Details soon. · More on Eclipse | — | Eclipse · Lần thứ nhất · Thứ Sáu 23/10 và Thứ Bảy 24/10/2026 · Eclipse là chuỗi sự kiện pop-up của Sol. Thông tin chi tiết sẽ sớm được cập nhật. · Xem thêm về Eclipse |
| / | the newsletter, now in the page (the footer's lines) and a visit block: Visit · Directions · Hours and address | — | Ghé thăm · Chỉ đường · Giờ mở cửa và địa chỉ |
| / | press quotes (full previews only): [A quote from a review, to come] · [Who, where, when] | — | [Trích dẫn từ một bài đánh giá, sẽ cập nhật] · [Ai, ở đâu, khi nào] |
| every page | header tab, now that its page exists: Events; footer, More: Press; (once public) Gift cards · Accessibility, and Privacy becomes the guests' notice with Applicant privacy beside it; the last line (once set): Tax code … | — | Sự kiện; Báo chí; Thẻ quà tặng · Hỗ trợ tiếp cận; Quyền riêng tư · Bảo mật cho ứng viên; MST … |
| /events/ | new page: Events · Eclipse · Eclipse is Sol’s pop-up series. · Coming up · Past editions | — | Sự kiện · Eclipse · Eclipse là chuỗi sự kiện pop-up của Sol. · Sắp diễn ra · Các lần trước |
| /events/ | each edition: Eclipse · First edition (Second … Tenth; then Edition 11) · its nights (three or more: Friday 23, Saturday 24 and Sunday 25 October 2026) · Details soon. · More | — | Eclipse · Lần thứ nhất (hai … mười; then Lần thứ 11) · Thứ Sáu 23/10 và Thứ Bảy 24/10/2026 (Thứ Sáu 23/10, Thứ Bảy 24/10 và Chủ Nhật 25/10/2026) · Thông tin chi tiết sẽ sớm được cập nhật. · Xem thêm |
| /events/ | when none is coming up: Nothing announced just now. Sign up for news by email, at the foot of the page, to hear about the next one. | — | Hiện chưa có lịch mới. Hãy đăng ký nhận tin qua email ở cuối trang để biết về lần tiếp theo. |
| /events/ | page title and description: Events — Sol, Tây Hồ · Eclipse, Sol’s pop-up series, at No 7, Lane 88 Quang An, Tây Hồ, Hanoi: what’s coming up, and what’s been. | — | Sự kiện — Sol, Tây Hồ · Eclipse, chuỗi sự kiện pop-up của Sol tại số 7, ngõ 88 Quảng An, Tây Hồ, Hà Nội: những gì sắp diễn ra và đã diễn ra. |
| /events/eclipse-1/ | an edition's page, once it has its line: When · Where · Sol, (the address) · Price · 850,000 VND a person · In the kitchen · The menu · Book · Book by email · This edition is over. · All editions | — | Thời gian · Địa điểm · Sol, (địa chỉ) · Giá · 850.000 đồng/người · Trong bếp · Thực đơn · Đặt chỗ · Đặt chỗ qua email · Eclipse lần này đã kết thúc. · Xem tất cả các lần Eclipse |
| /visit-us/ | Good to know, the questions waiting for answers (full previews only): Big groups · Getting here and parking · Step-free access and the lift · Paying · Bringing your own wine · What to wear · Dogs · Smoking; under the hours: Last orders [to come] | — | Nhóm đông · Đường đến và chỗ gửi xe · Lối vào không bậc thềm và thang máy · Thanh toán · Mang rượu vang riêng · Trang phục · Mang theo chó · Hút thuốc; Nhận gọi món đến [sẽ cập nhật] |
| /menu/ … | (once priced) Prices in Vietnamese đồng (VND). · a wine's prices: glass 120,000 · bottle 650,000 · Menu updated 13 October 2026. The wine page's last line drops “Prices are on the printed list in the room.” | — | Giá tính bằng đồng (VND). · ly 120.000 · chai 650.000 · Thực đơn cập nhật ngày 13/10/2026. (and drops “Giá có trên danh sách in tại nhà hàng.”) |
| /menu/ | the marks explained, English only: Veg vegetarian (Chay and Cay say it already) | — | — |
| /menu/ | (once some dishes are priced) the first-draft note loses “and prices here once they’re set” | (the note) | (the note, without “và giá sẽ được đăng ở đây khi đã chốt”) |
| /about/ | (full previews only) The dough · [The flours, the fermentation and the bake, in the kitchen’s words, to come] · the team's cards: Portrait · [A few lines, to come] · [What closing Sol Pizza meant to us, to come] | — | Bột bánh · [Bột mì, thời gian ủ và cách nướng, theo lời của bếp, sẽ cập nhật] · Chân dung · [Vài dòng giới thiệu, sẽ cập nhật] · [Việc đóng cửa Sol Pizza có ý nghĩa thế nào với chúng tôi, sẽ cập nhật] |
| /press/ | new page: Press · For the press · The facts, the logo, and who to ask. · The facts · The logo · Who to ask | — | Báo chí · Dành cho báo chí · Thông tin, logo và đầu mối liên hệ. · Thông tin · Logo · Liên hệ |
| /press/ | the facts: Name · What it is: An Italian-American restaurant: pizza from a wood-fired oven, pasta made in-house, and 30 wines, 26 of them by the glass. · Where · Opening: Soon · Hours · The oven: A Pavesi wood-fired oven, built in Italy. · Before Sol: Sol Pizza, in Tây Hồ until last year. · The kitchen: Ngọc runs the kitchen. · The company · Online | — | Tên · Sol là gì: Nhà hàng Ý–Mỹ: pizza lò củi, mì Ý làm tại nhà hàng và 30 loại vang, 26 loại có phục vụ theo ly. · Địa chỉ · Khai trương: Sắp tới · Giờ mở cửa · Lò nướng: Lò củi Pavesi, chế tác tại Ý. · Trước Sol: Sol Pizza, ở Tây Hồ cho đến năm ngoái. · Bếp: Ngọc phụ trách bếp. · Công ty · Trực tuyến |
| /press/ | In Sol red. Please use it as it is: don’t recolour, stretch or redraw it. · Download the logo (SVG) · Write to hello@sol.pizza. | — | Màu đỏ Sol. Vui lòng dùng nguyên bản: không đổi màu, kéo giãn hay vẽ lại. · Tải logo (SVG) · Hãy viết cho chúng tôi qua hello@sol.pizza. |
| /press/ | page title and description: Press — Sol, Tây Hồ · Sol for the press: the facts, the logo, and who to ask. An Italian-American restaurant at No 7, Lane 88 Quang An, Tây Hồ, Hanoi. | — | Báo chí — Sol, Tây Hồ · Thông tin về Sol dành cho báo chí: thông tin, logo và đầu mối liên hệ. Nhà hàng Ý–Mỹ tại số 7, ngõ 88 Quảng An, Tây Hồ, Hà Nội. |
| /gift-cards/ | (full previews only) Gift cards · Give someone dinner at Sol · A gift card for Sol, in Tây Hồ. · Values · How long a card lasts · How to buy one: At the restaurant, or by email: write to hello@sol.pizza. | — | Thẻ quà tặng · Tặng một bữa tối tại Sol · Thẻ quà tặng của Sol, ở Tây Hồ. · Mệnh giá · Thời hạn sử dụng · Cách mua: Tại nhà hàng, hoặc qua email: hãy viết cho chúng tôi qua hello@sol.pizza. |
| /privacy/guests/ | (full previews only) the guest privacy notice, a draft for the lawyer: Your privacy as our guest (also its page title) · What we keep, and why · Allergies and dietary needs · Who handles it for us · How long we keep it · Your rights · Questions. Every line is new; read it on the full preview | — | Quyền riêng tư của khách · Chúng tôi lưu gì, và vì sao · Dị ứng và chế độ ăn · Ai xử lý thông tin cho chúng tôi · Chúng tôi lưu trong bao lâu · Quyền của bạn · Câu hỏi |
| /accessibility/ | (full previews only) the accessibility statement, a draft for the lawyer: Accessibility · The website · Booking · The restaurant · Tell us. Every line is new; read it on the full preview | — | Hỗ trợ tiếp cận · Trang web · Đặt bàn · Nhà hàng · Hãy cho chúng tôi biết |
| /404 | It may have moved. Try one of these: (then the main pages) | — | Có thể trang đã được chuyển. Bạn hãy thử một trong những trang sau: |
| share cards | Events, new: Events · Tây Hồ, Hanoi / Eclipse, Sol’s pop-up series. | — | Sự kiện · Tây Hồ, Hà Nội / Eclipse, chuỗi pop-up của Sol. |

Questions for Linh:

1. **Pop-up.** “Eclipse là chuỗi sự kiện pop-up của Sol”: keep the English “pop-up”, as Hanoi restaurants do?
2. **The home eyebrow.** “Ẩm thực Ý–Mỹ · Tây Hồ, Hà Nội”: right for the first line a guest reads?
3. **The legal drafts.** “Quyền riêng tư của khách” and “Hỗ trợ tiếp cận” as titles; and the two drafts' wording, on the full preview, before the lawyer sees them.

## Booking, private dining and enquiries, 13 Oct 2026

A new page for groups and private dining, forms that write an email (the guest's email app opens with the details filled in, in the page's language), and a newsletter sign-up in every page's footer. Lines marked “(once online booking is live)” appear when the ResDiary widget goes on `/booking/`; “(full previews only)” are sections waiting for their content, never on sol.pizza until it arrives.

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| every page | header tab, now that its page exists: Private dining | — | Tiệc riêng |
| every page | footer: News from Sol · Events, new dishes and the next Eclipse, by email, now and then. · Sign up by email | — | Tin từ Sol · Sự kiện, món mới và Eclipse kế tiếp, thỉnh thoảng gửi qua email. · Đăng ký qua email |
| every page | the email the sign-up writes: Please add this email address to Sol’s newsletter. | — | Vui lòng thêm địa chỉ email này vào danh sách nhận tin của Sol. |
| every page | phone bar (once online booking is live): Zalo on Vietnamese pages, once we have the Zalo number; Call until then | — | Zalo; Gọi |
| /private-dining/ | new page: Private dining · Groups and private dining · For seven or more, or a night that’s all yours: tell us what you have in mind, and we’ll come back to you. | — | Tiệc riêng · Nhóm đông và tiệc riêng · Từ bảy người trở lên, hay một buổi tối chỉ dành riêng cho bạn: hãy cho chúng tôi biết bạn muốn tổ chức thế nào, chúng tôi sẽ liên hệ lại. |
| /private-dining/ | Tell us about it · The date, how many of you, and anything we should know. We’ll write back with what we can do. | — | Cho chúng tôi biết về buổi tiệc · Ngày nào, bao nhiêu người, và những điều chúng tôi nên biết. Chúng tôi sẽ phản hồi và cho bạn biết những gì chúng tôi có thể sắp xếp. |
| /private-dining/ | the form: Name · Phone or Zalo · Email · Date · Number of guests · The occasion · Budget per person · Anything else · (optional) · Send by email | — | Họ tên · Điện thoại hoặc Zalo · Email · Ngày · Số khách · Dịp tổ chức · Ngân sách mỗi người · Thông tin thêm · (không bắt buộc) · Gửi qua email |
| /private-dining/ | full previews only: The spaces (Ground floor · Upstairs · The whole restaurant) · Set menus (Menus and prices) · Minimum spend (For a private space) · [to come] | — | Không gian (Tầng 1 · Tầng 2 · Cả nhà hàng) · Thực đơn set (Thực đơn và giá) · Mức chi tối thiểu (Cho một không gian riêng) · [sẽ cập nhật] |
| /private-dining/ | page title and description: Private dining — Sol, Tây Hồ · Groups of seven or more and private dining at Sol, No 7, Lane 88 Quang An, Tây Hồ, Hanoi. Tell us what you have in mind. | — | Tiệc riêng — Sol, Tây Hồ · Nhóm từ bảy người trở lên và tiệc riêng tại Sol, số 7, ngõ 88 Quảng An, Tây Hồ, Hà Nội. Hãy cho chúng tôi biết bạn muốn tổ chức thế nào. |
| /private-dining/, /booking/ | under each form: This opens your email app with the details filled in: send it from there. Or write to us at hello@sol.pizza. | — | Nút này mở ứng dụng email với nội dung đã điền sẵn: bạn chỉ cần gửi đi. Hoặc viết cho chúng tôi qua hello@sol.pizza. |
| /private-dining/, /booking/ | after Send: Your email app should have opened with your message. If it didn’t, copy the message below and send it to hello@sol.pizza. The box with the message, for screen readers: Your message; in the box: To: · Subject: | — | Ứng dụng email của bạn lẽ ra đã mở với nội dung điền sẵn. Nếu chưa thấy, hãy sao chép nội dung dưới đây và gửi tới hello@sol.pizza.; Nội dung email; Gửi tới: · Tiêu đề: |
| /booking/ | until online booking is live: Hold me a table for opening week · Tell us who’s coming and when, and we’ll write back to confirm. | — | Giữ bàn cho tôi trong tuần khai trương · Hãy cho chúng tôi biết bạn đi mấy người và vào tối nào, chúng tôi sẽ trả lời để xác nhận. |
| /booking/ | its form: Name · Phone or Zalo · Email · Number of guests · Which night, and roughly what time · Anything else · Send by email | — | Họ tên · Điện thoại hoặc Zalo · Email · Số khách · Tối nào, khoảng mấy giờ · Thông tin thêm · Gửi qua email |
| /booking/, /visit-us/ | Seven or more? Tell us about your group and we’ll look after you personally. (The link goes to the private dining form.) | Nhóm từ bảy người trở lên: vui lòng gửi email, chúng tôi sẽ sắp xếp riêng cho bạn. | Nhóm từ bảy người trở lên? Hãy cho chúng tôi biết về nhóm của bạn, chúng tôi sẽ sắp xếp riêng. |
| /booking/ | under the widget (once online booking is live): Trouble with the booking form? Phone · Zalo · email. | — | Không đặt được qua biểu mẫu? (the same links) |
| /booking/ | the contact list (once online booking is live, and once we have the numbers): Zalo · WhatsApp, between Phone and Email | — | Zalo · WhatsApp (names stay as written) |
| /booking/ | full previews only: Before you book · Cancellations · Deposits · How long a table is yours · Booking online · [to come] | — | Trước khi đặt bàn · Hủy bàn · Đặt cọc · Thời gian giữ bàn · Đặt bàn trực tuyến · [sẽ cập nhật] |
| share cards | private dining, new, in both languages: Private dining · Tây Hồ, Hanoi / Groups and private dining. | — | Tiệc riêng · Tây Hồ, Hà Nội / Nhóm đông và tiệc riêng. |

Questions for Linh:

1. **Floors.** The private dining spaces will be named by floor: “Tầng 1” for the ground floor and “Tầng 2” upstairs, as Hanoi counts them. Right, or “Tầng trệt” and “Tầng 1”?
2. **Newsletter.** “Tin từ Sol” for News from Sol, and “danh sách nhận tin” for the newsletter: natural?

## Vietnamese addresses, the new header, cookies, 13 Oct 2026

Every page now has its own Vietnamese address: `/vi/` for the home page, `/vi/menu/`, `/vi/about/` and so on. The Vietnamese is the same as before unless listed here; it just isn't in the English page any more. EN · VI are now links to the same page in the other language. Lines marked “(with a date)” or “(once open)” appear only when the opening date is set, or from opening day.

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| every page | header tabs: Menu · About · Visit (Booking is now the red button; Events and Private dining come with their pages) | Giới thiệu · Thực đơn · Đặt bàn | Thực đơn · Giới thiệu · Ghé thăm |
| every page | header tabs still to come: Events · Private dining | — | Sự kiện · Tiệc riêng |
| every page | red button in the header and the menu sheet: Book; Book a table | — | Đặt bàn; Đặt bàn |
| every page | phone bar: Book · Directions (· Call, once online booking is live); its label for screen readers: Quick actions | — | Đặt bàn · Chỉ đường (· Gọi); Thao tác nhanh |
| every page | footer, More: Booking · Cookies; and Cookie settings at the end of the last line | — | Đặt bàn · Cookie; Cài đặt cookie |
| every page | cookie banner heading: Cookies | — | Cookie |
| every page | cookie banner: We’d like to use analytics cookies to see how the site is used, and advertising cookies to see whether our ads work. The site works the same without them, and you can change your mind any time under Cookie settings. | — | Chúng tôi muốn dùng cookie phân tích để biết trang web được sử dụng ra sao, và cookie quảng cáo để biết quảng cáo của chúng tôi có hiệu quả không. Trang web vẫn hoạt động như bình thường nếu không có chúng, và bạn có thể đổi lựa chọn bất cứ lúc nào ở mục Cài đặt cookie. |
| every page | cookie banner link: Cookie notice | — | Thông báo về cookie |
| every page | cookie banner choices: Analytics — Google Analytics: which pages are read, and how people find us. · Advertising — Meta Pixel: whether our ads on Facebook and Instagram bring people to the site. | — | Phân tích — Google Analytics: những trang nào được đọc, và khách tìm đến chúng tôi bằng cách nào. · Quảng cáo — Meta Pixel: quảng cáo của chúng tôi trên Facebook và Instagram có đưa khách đến trang web không. |
| every page | cookie banner buttons: Accept all · Reject all · Settings · Save choices | — | Đồng ý tất cả · Từ chối tất cả · Tùy chọn · Lưu lựa chọn |
| every page | announcement bar, for screen readers: Announcement · Dismiss | — | Thông báo · Đóng thông báo |
| every page | footer, last orders (once the time is set): Last orders 10pm | — | Nhận gọi món đến 22:00 |
| / | eyebrow (with a date): Opening Thursday 5 November · Tây Hồ, Hanoi; (once open): Tây Hồ, Hanoi | Sắp khai trương · Tây Hồ, Hà Nội | Khai trương thứ Năm 05/11 · Tây Hồ, Hà Nội; Tây Hồ, Hà Nội |
| / | facts, Opening (with a date): Thu 5 Nov; the fact goes once open | Sắp tới | thứ Năm 05/11 |
| / | lead (once open): Sol Pizza closed last year. Sol is open on the same stretch of Tây Hồ with more room: … | Sol Pizza đã đóng cửa năm ngoái. Sol sẽ mở lại ngay trên con phố ấy ở Tây Hồ, … | Sol Pizza đã đóng cửa năm ngoái. Sol đã mở cửa ngay trên con phố ấy ở Tây Hồ, với nhiều không gian hơn: căn bếp rộng hơn, một quầy bar đúng nghĩa và chiếc lò củi Pavesi chế tác tại Ý. |
| / | meta description (with a date): …Sol opens on Thursday 5 November at No 7…; (once open): …26 wines by the glass at No 7, Lane 88 Quang An, Tây Hồ, Hanoi. | …Sol sắp khai trương tại số 7… | …Sol khai trương thứ Năm 05/11 tại số 7, ngõ 88 Quảng An, Tây Hồ, Hà Nội.; …26 loại vang theo ly, tại số 7, ngõ 88 Quảng An, Tây Hồ, Hà Nội. |
| /visit-us/ | new page, from the Booking page: Visit · Find us · Sol is on the first two floors of No 7, Lane 88 Quang An. We’re opening soon. · the hours, address, contact and Good to know, then a Book a table box with the line for seven or more | Ghé thăm · Tìm chúng tôi và đặt bàn · (the rest as on Booking) | Ghé thăm · **Tìm chúng tôi** · (the rest unchanged) |
| /visit-us/ | page title and description: Visit — Sol, Tây Hồ · Sol is at No 7, Lane 88 Quang An Street, Tây Hồ, Hanoi. Open Tuesday to Sunday, 5pm–11pm, from the day we open. | — | Ghé thăm — Sol, Tây Hồ · Sol ở số 7, ngõ 88 Quảng An, Tây Hồ, Hà Nội. Mở cửa Thứ Ba đến Chủ Nhật, 17:00 – 23:00, kể từ ngày khai trương. |
| /booking/ | the page is now the booking box: Reservations · Book a table · the booking line, then phone, email and Instagram | Ghé thăm · Tìm chúng tôi và đặt bàn | Đặt chỗ · Đặt bàn · (the booking line unchanged) |
| /booking/ | under the box: Tuesday to Sunday, 5pm–11pm, from the day we open · the address; link: Hours, address and getting here | — | Thứ Ba đến Chủ Nhật, 17:00 – 23:00, kể từ ngày khai trương · Số 7, Ngõ 88 Quảng An, Tây Hồ, Hà Nội; Giờ mở cửa, địa chỉ và đường đến |
| /booking/ | meta description (once online booking is live): … Book online, or call or email us. | — | … Đặt bàn trực tuyến, hoặc gọi điện hay gửi email. |
| /booking/ | lead (once open, until online booking is live): Call or email us and we’ll hold you a table. | — | Hãy gọi điện hoặc gửi email, chúng tôi sẽ giữ bàn cho bạn. |
| /menu/wine/, /menu/bar/ | Good to know, a new last line: We don’t serve alcohol to anyone under 18. If you’ve been drinking, please don’t drive. | — | Không bán rượu, bia cho người dưới 18 tuổi. Đã uống rượu, bia thì không lái xe. |
| /jobs/ | after the round closed: eyebrow Work with us · Tây Hồ, Hanoi; the lead becomes the closed line (already on the cards); meta description: Work with Sol in Tây Hồ, Hanoi. Applications for our opening team closed on Sunday 4 October 2026. | Tuyển dụng · Tây Hồ, Hà Nội; Chúng tôi sắp khai trương. Bếp và khu phục vụ đang tuyển ngay bây giờ…; Chúng tôi đang tuyển Lễ tân (Host)… | Tuyển dụng · Tây Hồ, Hà Nội; Đợt tuyển dụng này đã đóng vào Chủ nhật 04/10/2026. Cảm ơn tất cả các bạn đã ứng tuyển.; Làm việc cùng Sol tại Tây Hồ, Hà Nội. Đợt tuyển đội ngũ khai trương đã đóng vào Chủ nhật 04/10/2026. |
| /about/ | Build it with us: only while a hiring round is open (gone now); We’re still building…: goes on opening day | (unchanged) | (unchanged) |
| /privacy/cookies/ | new page: Privacy · Cookies on sol.pizza · Last updated 13 October 2026 | — | Bảo mật · Cookie trên sol.pizza · Cập nhật lần cuối: 13/10/2026 |
| /privacy/cookies/ | sol.pizza is the website of Sol, a restaurant run by Công ty TNHH Aurelian (Aurelian Company Limited) at No 7, Lane 88 Quang An Street, Tây Hồ, Hanoi. This notice lists what the site keeps in your browser, and the choice you have about it. It follows the Law on Personal Data Protection No. 91/2025/QH15 and Decree 356/2025/ND-CP. | — | sol.pizza là trang web của Sol, nhà hàng do Công ty TNHH Aurelian điều hành tại số 7, ngõ 88 Quảng An, Tây Hồ, Hà Nội. Thông báo này liệt kê những gì trang web lưu trong trình duyệt của bạn, và lựa chọn của bạn về việc đó, theo Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15 và Nghị định 356/2025/NĐ-CP. |
| /privacy/cookies/ | Always on · The site needs these to remember what you chose. They stay in your browser and tell us nothing about you. | — | Luôn bật · Trang web cần những mục này để nhớ lựa chọn của bạn. Chúng nằm trong trình duyệt của bạn và không cho chúng tôi biết gì về bạn. |
| /privacy/cookies/ | table headings: Name · What it does · How long · Whose | — | Tên · Dùng để làm gì · Lưu bao lâu · Của ai |
| /privacy/cookies/ | rows: Your cookie choice · The language you picked · That you closed an announcement · Security: tells people from automated traffic. Set by Cloudflare, which serves the site. · 12 months · Until you clear it | — | Lựa chọn cookie của bạn · Ngôn ngữ bạn đã chọn · Bạn đã đóng một thông báo · Bảo mật: phân biệt người dùng với truy cập tự động. Do Cloudflare, đơn vị vận hành máy chủ của trang, thiết lập. · 12 tháng · Đến khi bạn xoá |
| /privacy/cookies/ | Analytics: only if you say yes · Google Analytics shows us which pages are read and how people find us. Google may process this data outside Vietnam. · Counts visits, and tells one visitor from another · Up to 2 years | — | Phân tích: chỉ khi bạn đồng ý · Google Analytics cho chúng tôi biết những trang nào được đọc và khách tìm đến chúng tôi bằng cách nào. Google có thể xử lý dữ liệu này ở ngoài Việt Nam. · Đếm lượt truy cập, và phân biệt các khách truy cập · Tối đa 2 năm |
| /privacy/cookies/ | Advertising: only if you say yes · The Meta Pixel tells us whether our ads on Facebook and Instagram bring people to the site. Meta may process this data outside Vietnam. · Recognise a visit that came from one of our ads · Where the visit came from · 90 days | — | Quảng cáo: chỉ khi bạn đồng ý · Meta Pixel cho chúng tôi biết quảng cáo trên Facebook và Instagram có đưa khách đến trang web không. Meta có thể xử lý dữ liệu này ở ngoài Việt Nam. · Nhận biết lượt truy cập đến từ quảng cáo của chúng tôi · Lượt truy cập đến từ đâu · 90 ngày |
| /privacy/cookies/ | Your choice · Nothing in Analytics or Advertising loads until you choose, and the site works the same whichever you choose. Change your mind any time with Cookie settings at the foot of every page: if you take back a yes, we remove those cookies and stop loading the tool. We ask again after 12 months. | — | Lựa chọn của bạn · Không có mục Phân tích hay Quảng cáo nào được tải trước khi bạn chọn, và trang web hoạt động như nhau dù bạn chọn thế nào. Bạn có thể đổi lựa chọn bất cứ lúc nào ở mục Cài đặt cookie cuối mỗi trang: nếu bạn rút lại sự đồng ý, chúng tôi xoá các cookie đó và ngừng tải công cụ tương ứng. Sau 12 tháng, chúng tôi sẽ hỏi lại. |
| /privacy/cookies/ | Questions · Write to hello@sol.pizza. If you applied for a job with us, the applicant privacy notice explains how we handle your application. | — | Câu hỏi · Hãy viết cho chúng tôi qua hello@sol.pizza. Nếu bạn đã ứng tuyển tại Sol, thông báo bảo mật dành cho ứng viên giải thích cách chúng tôi xử lý hồ sơ của bạn. |
| /privacy/cookies/ | page title and description: Cookies — Sol · What sol.pizza keeps in your browser, and how to change your choice. | — | Cookie — Sol · Những gì sol.pizza lưu trong trình duyệt của bạn, và cách thay đổi lựa chọn. |
| share cards | the Vietnamese cards, new (the English ones were the only ones): home · menu · wine · about · visit and booking · jobs | — | Tây Hồ, Hà Nội / Ẩm thực Ý–Mỹ, nấu bằng lửa củi. · Thực đơn · Lò củi, làm tại nhà hàng / Chúng tôi nấu gì. · Danh sách vang · Theo ly và theo chai / Hỏi xem tối nay mở chai nào. · Câu chuyện của chúng tôi · Sol, Tây Hồ / Khép lại một điều, để dựng nên điều mới. · Tây Hồ, Hà Nội / Tìm chúng tôi và đặt bàn. · Tuyển dụng · Tây Hồ, Hà Nội / Cùng xây dựng Sol mới. |
| full build only | the label on a section waiting for content: Content needed; the components page (`/styleguide/`) | — | Cần nội dung; (its example lines, never on sol.pizza) |

Questions for Linh:

1. **Tabs.** “Ghé thăm” for Visit (as the Booking page’s old eyebrow) and “Tiệc riêng” for Private dining: right, or would “Phòng riêng” read better?
2. **Cookie.** The banner keeps the word “cookie”, as most Vietnamese sites do. Fine?

## The kitchen: dough calculator and dough log, 6 Oct 2026

New pages for the kitchen, behind the kitchen password and out of search: the dough calculator (`/dough/`), the dough log (`/dough/log/`) and the sign-in page (`/dough/login/`). Every line is new. Numbers follow the language: 6,301 g and 2.8 in English, 6.301 g and 2,8 in Vietnamese; the log’s day headings are written by the browser (“Thứ Ba, 6 tháng 10, 2026”). Poolish and biga stay as written.

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| /dough/ | eyebrow on the kitchen pages: Kitchen | — | Bếp |
| /dough/ | heading and page title: Dough calculator; Dough calculator — Sol | — | Tính bột pizza; Tính bột pizza — Sol |
| /dough/ | lead: Set the number of balls and their weight, and the weights for the mix follow. | — | Nhập số viên bột và trọng lượng mỗi viên, lượng nguyên liệu cần trộn sẽ tự tính. |
| /dough/ | meta description: The dough calculator for Sol’s kitchen. | — | Công cụ tính bột pizza cho bếp của Sol. |
| /dough/ | kitchen menu: Calculator · Dough log · Sign out | — | Tính bột · Nhật ký bột · Đăng xuất |
| /dough/ | without JavaScript: The calculator needs JavaScript. Turn it on in the browser’s settings. | — | Công cụ này cần JavaScript. Hãy bật JavaScript trong cài đặt trình duyệt. |
| /dough/ | The batch · Dough balls · Each ball · Waste | — | Mẻ bột · Số viên bột · Mỗi viên · Hao hụt |
| /dough/ | Waste: extra dough for what stays in the mixer bowl and on the bench. | — | Hao hụt: phần bột làm thêm cho lượng dính lại trong cối trộn và trên bàn. |
| /dough/ | The formula · Hydration · Salt · Fresh yeast · Oil · Sugar | — | Công thức · Tỉ lệ nước · Muối · Men tươi · Dầu · Đường |
| /dough/ | Baker’s percentages: each ingredient as a percentage of all the flour’s weight. | — | Tỉ lệ theo bột mì (baker’s percentage): mỗi nguyên liệu tính bằng phần trăm so với tổng trọng lượng bột mì. |
| /dough/ | The flour · Pizza flour · Whole wheat · Rye | — | Bột mì · Bột pizza · Nguyên cám · Lúa mạch đen |
| /dough/ | Pizza flour is the rest. A preferment is made with pizza flour; whole wheat and rye go in at the final mix. | — | Bột pizza là phần còn lại. Bột ủ làm bằng bột pizza; bột nguyên cám và lúa mạch đen cho vào ở lần trộn chính. |
| /dough/ | Preferment: None · Poolish · Biga | — | Bột ủ trước: Không · Poolish · Biga |
| /dough/ | Share of the flour · Its hydration · Its yeast | — | Phần bột mì · Tỉ lệ nước · Men tươi |
| /dough/ | Share of the flour: how much of all the flour goes into the preferment. Its fresh yeast is a percentage of its own flour. The salt and the rest go in at the final mix. | — | Phần bột mì: bao nhiêu phần trăm tổng lượng bột mì dùng cho bột ủ. Men tươi của bột ủ tính theo phần trăm bột mì của chính nó. Muối và phần còn lại cho vào ở lần trộn chính. |
| /dough/ | The kitchen · Temperature · Air humidity | — | Bếp · Nhiệt độ · Độ ẩm không khí |
| /dough/ | Measure them when you mix. Both go in the log, and the temperature works out the water. | — | Đo khi bắt đầu trộn. Cả hai được ghi vào nhật ký, và nhiệt độ bếp dùng để tính nhiệt độ nước. |
| /dough/ | Water temperature | — | Nhiệt độ nước |
| /dough/ | Measure the flour and your water too, and this works out how warm the water should be, and how much ice, for the dough you want. | — | Đo thêm nhiệt độ bột mì và nước, công cụ sẽ tính nước cần ấm hay lạnh bao nhiêu, và cần bao nhiêu đá, để bột đạt nhiệt độ mong muốn. |
| /dough/ | Dough to aim for · Flour · Preferment · Mixer friction · Your water | — | Bột cần đạt · Bột mì · Bột ủ · Nhiệt từ máy trộn · Nước của bạn |
| /dough/ | Mixer friction: how much the mixer warms the dough. To measure it, after a mix: 3 × the dough’s temperature, minus the flour, the kitchen and the water (with a preferment, 4 × and minus the preferment too). | — | Nhiệt từ máy trộn: máy trộn làm bột ấm thêm bao nhiêu độ. Cách đo, sau một mẻ trộn: 3 × nhiệt độ bột, trừ nhiệt độ bột mì, bếp và nước (nếu có bột ủ: 4 × và trừ thêm nhiệt độ bột ủ). |
| /dough/ | Your water: as it comes, from the tap or the fridge, before any ice. | — | Nước của bạn: nhiệt độ nước đang có, từ vòi hoặc tủ lạnh, trước khi cho đá. |
| /dough/ | results: Weigh out · 60 × 260 g · 15.9 kg of dough, with 2% for waste | — | Cân nguyên liệu · 60 × 260 g · 15,9 kg bột, đã gồm 2% hao hụt |
| /dough/ | results: Poolish · mix first · Final mix · All the poolish | — | Poolish · trộn trước · Trộn chính · Toàn bộ poolish |
| /dough/ | results: Pizza flour · Whole wheat flour · Rye flour · Water · Salt · Fresh yeast · Oil · Sugar · Total | — | Bột pizza · Bột mì nguyên cám · Bột lúa mạch đen · Nước · Muối · Men tươi · Dầu · Đường · Tổng |
| /dough/ | results: 2,785 g water + 520 g ice · 3,314 g water at 30 °C | — | 2.785 g nước + 520 g đá · 3.314 g nước ở 30 °C |
| /dough/ | results: For dough at 24 °C the water works out at 11 °C; yours is 28 °C. | — | Để bột đạt 24 °C, nước cần ở 11 °C; nước của bạn đang ở 28 °C. |
| /dough/ | results: Measure the kitchen’s temperature to work out the water. | — | Hãy đo nhiệt độ bếp để tính nhiệt độ nước. |
| /dough/ | Check the marked boxes. | — | Kiểm tra lại các ô được đánh dấu. |
| /dough/ | Whole wheat and rye come to more than all the flour. | — | Bột nguyên cám và bột lúa mạch đen đang nhiều hơn tổng lượng bột mì. |
| /dough/ | The preferment needs more pizza flour than the blend has. Lower its share of the flour, or the whole wheat and rye. | — | Bột ủ cần nhiều bột pizza hơn lượng có trong hỗn hợp. Hãy giảm phần bột mì của bột ủ, hoặc giảm bột nguyên cám và lúa mạch đen. |
| /dough/ | The preferment holds more water than the whole dough. Lower its hydration or its share of the flour. | — | Bột ủ đang chứa nhiều nước hơn cả khối bột. Hãy giảm tỉ lệ nước hoặc phần bột mì của bột ủ. |
| /dough/ | Ice alone can’t cool it that far: chill the flour first, or aim a degree or two warmer. | — | Chỉ dùng đá thì không đủ lạnh: hãy làm lạnh bột mì trước, hoặc chọn nhiệt độ bột cao hơn một, hai độ. |
| /dough/ | Water above 40 °C can harm the yeast: use it cooler and let the dough warm up after mixing. | — | Nước trên 40 °C có thể làm hỏng men: hãy dùng nước nguội hơn và để bột ấm lên sau khi trộn. |
| /dough/ | All the water is in the preferment, so there’s none to set at the final mix. | — | Toàn bộ nước đã nằm trong bột ủ, nên không có nước để điều chỉnh ở lần trộn chính. |
| /dough/ | buttons: Share this batch · Link copied · Back to the house spec · Log this batch | — | Chia sẻ mẻ bột này · Đã sao chép liên kết · Về công thức chuẩn · Ghi nhật ký mẻ này |
| /dough/ | The page opens on the house spec. Share sends the batch as it is now, as a link. | — | Trang luôn mở với công thức chuẩn của bếp. Nút Chia sẻ gửi mẻ bột hiện tại dưới dạng liên kết. |
| /dough/ | Log this batch · Once it’s mixed. The batch, the flour, the kitchen and the weights above go in with it. | — | Ghi nhật ký mẻ này · Sau khi trộn xong. Mẻ bột, bột mì, thông số bếp và lượng nguyên liệu ở trên sẽ được ghi cùng. |
| /dough/ | Day · Mixed by · Dough after mixing · Notes · button: Log this batch | — | Ngày · Người trộn · Bột sau khi trộn · Ghi chú · Ghi vào nhật ký |
| /dough/ | Measure the kitchen first: its temperature and air humidity go in the log. | — | Hãy đo bếp trước: nhiệt độ và độ ẩm không khí sẽ được ghi vào nhật ký. |
| /dough/ | Add the day and who mixed it. · Fix what’s marked above first. | — | Hãy ghi ngày và người trộn. · Hãy sửa các mục được đánh dấu ở trên trước. |
| /dough/ | Saving… · Logged. See the dough log | — | Đang lưu… · Đã ghi. Xem nhật ký bột |
| /dough/ | Couldn’t save it. Check the connection and try again. | — | Chưa lưu được. Hãy kiểm tra kết nối và thử lại. |
| /dough/ | You’ve been signed out. Sign in in a new tab, then log it again here. | — | Bạn đã bị đăng xuất. Hãy đăng nhập ở một thẻ mới, rồi ghi lại ở đây. |
| /dough/ | The log isn’t set up on this copy of the site. | — | Nhật ký chưa được thiết lập trên bản này của trang. |
| /dough/log/ | heading and page title: Dough log; Dough log — Sol | — | Nhật ký bột; Nhật ký bột — Sol |
| /dough/log/ | lead: Every batch logged from the calculator, newest first. | — | Mọi mẻ bột đã ghi từ công cụ tính bột, mới nhất ở trên. |
| /dough/log/ | meta description: Every batch of dough logged in Sol’s kitchen. | — | Nhật ký các mẻ bột của bếp Sol. |
| /dough/log/ | Download it as a spreadsheet (CSV) | — | Tải về dạng bảng tính (CSV) |
| /dough/log/ | Loading… · Nothing logged yet. Log a batch from the calculator. | — | Đang tải… · Chưa có gì trong nhật ký. Hãy ghi một mẻ từ công cụ tính bột. |
| /dough/log/ | Couldn’t load the log. Check the connection and reload the page. · Couldn’t delete it. Check the connection and try again. | — | Không tải được nhật ký. Hãy kiểm tra kết nối và tải lại trang. · Chưa xoá được. Hãy kiểm tra kết nối và thử lại. |
| /dough/log/ | You’ve been signed out. Sign in again. | — | Bạn đã bị đăng xuất. Đăng nhập lại. |
| /dough/log/ | each batch: Test cook, logged at 12:28 | — | Test cook, ghi lúc 12:28 |
| /dough/log/ | each batch: Flour · Formula · Preferment · Kitchen · Water · Dough after mixing · Weighed out · Notes | — | Bột mì · Công thức · Bột ủ trước · Bếp · Nước · Bột sau khi trộn · Đã cân · Ghi chú |
| /dough/log/ | each batch: 85% pizza flour · 10% whole wheat · 5% rye | — | 85% bột pizza · 10% nguyên cám · 5% lúa mạch đen |
| /dough/log/ | each batch: Hydration 65% · salt 2.8% · fresh yeast 0.6% · oil · sugar | — | Nước 65% · muối 2,8% · men tươi 0,6% · dầu · đường |
| /dough/log/ | each batch: Poolish: 30% of the flour, 100% hydration, 0.3% fresh yeast | — | Poolish: 30% bột mì, 100% nước, 0,3% men tươi |
| /dough/log/ | each batch: 29 °C · air humidity 78% · 11 °C, with 520 g ice · 24.5 °C (aiming for 24 °C) | — | 29 °C · độ ẩm không khí 78% · 11 °C, có 520 g đá · 24,5 °C (mục tiêu 24 °C) |
| /dough/log/ | each batch: Delete · Delete this batch from the log? This can’t be undone. · Show older batches | — | Xoá · Xoá mẻ này khỏi nhật ký? Không thể hoàn tác. · Xem các mẻ cũ hơn |
| /dough/login/ | heading: Sign in; page title: Sign in — Sol kitchen | — | Đăng nhập; Đăng nhập — Bếp Sol |
| /dough/login/ | The dough calculator and the dough log are for Sol’s kitchen. Ask the Sous Chef for the password. | — | Công cụ tính bột và nhật ký bột dành cho bếp của Sol. Hãy hỏi Bếp phó để biết mật khẩu. |
| /dough/login/ | meta description: Sign in to Sol’s kitchen tools. | — | Đăng nhập vào công cụ của bếp Sol. |
| /dough/login/ | Kitchen password · button: Sign in | — | Mật khẩu bếp · Đăng nhập |
| /dough/login/ | That isn’t the password. Try again. | — | Mật khẩu chưa đúng. Hãy thử lại. |
| /dough/login/ | Too many tries. Wait 15 minutes, then try again. | — | Bạn đã thử quá nhiều lần. Hãy đợi 15 phút rồi thử lại. |
| /dough/login/ | Signing in isn’t set up on this copy of the site. | — | Chức năng đăng nhập chưa được thiết lập trên bản này của trang. |
| /dough/login/ | You stay signed in on this phone for 30 days. | — | Bạn sẽ được giữ đăng nhập trên điện thoại này trong 30 ngày. |
| all three | for screen readers, after each box’s label: grams · percent · degrees Celsius | — | gam · phần trăm · độ C |

To check with the kitchen: the words the team actually uses for whole wheat (“nguyên cám”), rye (“lúa mạch đen”), hydration (“tỉ lệ nước”), preferment (“bột ủ trước”), waste (“hao hụt”) and mixer friction (“nhiệt từ máy trộn”), and whether “Bột pizza” is what they call the pizza flour.
## Whole site public again, 6 Oct 2026

The hiring round has closed, and sol.pizza shows every page again: About, Menu (Food, Wine, Bar) and Booking are back, with their Vietnamese as before 27 September (as on the full-site preview). No Vietnamese text is new or changed. The 27 Sep changes below are undone: the header tabs are “Giới thiệu · Thực đơn · Đặt bàn” again (no “Tuyển dụng” tab; it stays in the footer’s “Thêm” column), the home buttons are “Đặt bàn” and “Xem thực đơn”, and the 404 buttons “Thực đơn” and “Đặt bàn”, so “Trang chủ” no longer shows.

## Home tagline, 28 Sep 2026

The hand-written line under the home page heading changed (both the public site and the full site).

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| / | sunshine, after dark (was “with the oven we always wanted”) | cùng chiếc lò chúng tôi luôn mong muốn | ánh nắng, sau hoàng hôn |

## Public site: home page and jobs, 27 Sep 2026

Until the rest of the site is ready, sol.pizza shows the home page and the jobs section only (`/jobs/`, the role pages, `/privacy/`). About, Menu and Booking are unchanged and stay on the full-site preview (https://full-site-sol-pizza.polarized-jar.workers.dev), which still shows every page and line as before. On sol.pizza, these lines are new or in a new place. Only “Trang chủ” is new text; the others are already on the site.

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| every page | header tab: Work with us (the only tab; also the only link in the mobile menu) | — (the tabs were Giới thiệu · Thực đơn · Đặt bàn) | Tuyển dụng (as in the footer) |
| / | red button: See open roles (replaces “Book a table”) | Đặt bàn | Xem vị trí tuyển dụng (as on /about/ and the role pages) |
| / | outline button: @solhanoi on Instagram (replaces “See the menu”) | Xem thực đơn | @solhanoi trên Instagram (as in the footer) |
| /404 | red button: Home (replaces “Menu”) | Thực đơn | Trang chủ |
| /404 | outline button: See open roles (replaces “Booking”) | Đặt bàn | Xem vị trí tuyển dụng |

Not on sol.pizza for now (still on the full-site preview, unchanged): the header tabs “Giới thiệu”, “Thực đơn”, “Đặt bàn” and the Food / Wine / Bar tabs under Thực đơn; the same three links in the footer’s “Thêm” column, which now lists “Tuyển dụng” and “Bảo mật”; the home buttons “Đặt bàn” and “Xem thực đơn”; the 404 buttons “Thực đơn” and “Đặt bàn”.

## Jobs: the opening team, 24 Sep 2026

The six opening-team roles now have a card each on `/jobs/` and a page each at `/jobs/<slug>/` (`host`, `server`, `bartender`, `pizzaiolo`, `line-cook`, `kitchen-porter`), in both languages.

Not listed line by line, because they are the approved text from the hiring brief: the Vietnamese job descriptions on the six pages (`build/jobs/<slug>.md`), the card lines and apply questions (`build/jobs-data.json`), and the labels the brief gave. Those labels are “Bộ phận phục vụ”, “Bếp”, “+ phí phục vụ & tip ước tính 2.000.000 – 4.000.000 VNĐ/tháng”, “Số lượng: 2”, “Hạn nộp: Chủ nhật 04/10 · Bắt đầu: thứ Hai 12/10”, “Xem mô tả công việc”, “Ứng tuyển”, the closed note “Đợt tuyển dụng này đã đóng vào Chủ nhật 04/10/2026. Cảm ơn tất cả các bạn đã ứng tuyển.”, and the Apply email (“Họ tên: / Số điện thoại / Zalo: / … / Câu trả lời của bạn: / (Vui lòng đính kèm CV.)”). New and changed lines that aren’t from the brief:

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| /jobs/ | benefit: A share of the 5% service charge and the tip pool for floor and kitchen roles, paid quarterly, starting once we open. [was “A share of the 5% service charge and the tip pool, paid quarterly, for floor and kitchen roles.”] | Một phần trong 5% phí phục vụ và quỹ tip của nhà hàng, trả hàng quý, cho các vị trí phục vụ và bếp. | Một phần trong 5% phí phục vụ và quỹ tip cho các vị trí phục vụ và bếp, trả hàng quý, bắt đầu khi nhà hàng mở cửa. |
| /jobs/ | card: Base salary 9,000,000–10,000,000 VND gross a month | — | Lương cơ bản 9.000.000 – 10.000.000 VNĐ gross/tháng |
| /jobs/ | card: the Vietnamese title under the English one (English view only), e.g. Lễ tân nhà hàng | — | the role’s Vietnamese title without “(Host)” and the like |
| /jobs/ | card links, for screen readers only: Read the role: Host · Apply: Host | — | Xem mô tả công việc: Lễ tân nhà hàng (Host) · Ứng tuyển: Lễ tân nhà hàng (Host) (the role’s Vietnamese title after the colon) |
| role pages | fact: Service charge & tips · Est. 2,000,000 – 4,000,000 VND per month, starting once we open | — | Phí phục vụ & tip · Ước tính 2.000.000 – 4.000.000 VNĐ/tháng, bắt đầu khi nhà hàng mở cửa |
| role pages | fact: Typical monthly total · 11,000,000 – 14,000,000 VND | — | Tổng thu nhập hằng tháng (ước tính) · 11.000.000 – 14.000.000 VNĐ |
| role pages | Read the full job description (the fold) | — | Xem toàn bộ mô tả công việc |
| role pages | See open roles (button at the end) | — | Xem vị trí tuyển dụng (as on /about/) |
| role pages | page title: Pizzaiolo — Sol, Tây Hồ | — | Đầu bếp Pizza (Pizzaiolo) — Sol, Tây Hồ (the role’s Vietnamese title) |
| role pages | meta description: Pizzaiolo at Sol, Tây Hồ, Hanoi. Base salary 11,000,000–14,000,000 VND a month, plus service charge and tips, est. 2,000,000–4,000,000 VND a month. Applications close Sunday 4 October 2026. | — | Tuyển Đầu bếp Pizza (Pizzaiolo) tại Sol, Tây Hồ, Hà Nội. Lương cơ bản 11–14 triệu + phí phục vụ ước tính 2–4 triệu/tháng. Hạn nộp 04/10/2026. |
| role pages | share card (Vietnamese only, the brief’s pattern) | — | Tuyển Pizzaiolo — Sol, Tây Hồ · Lương cơ bản 11–14 triệu + phí phục vụ ước tính 2–4 triệu/tháng. Hạn nộp 04/10/2026. |

No longer on the site:

- /jobs/: the Host card (“Khu phục vụ · Toàn thời gian”, “Lễ tân (Host)”, its description, its pay line and “Ứng tuyển: gửi email tới jobs@sol.pizza, tiêu đề ghi “Host””), now the Host card and page above. The page’s meta description, unchanged, still says “Chúng tôi đang tuyển Lễ tân (Host) và đội ngũ khai trương…”.
- /jobs/: the “Opening team” card (“Phục vụ và bếp”, “Đội ngũ khai trương” and its description, which listed baristas).
- /jobs/: the benefit “Được tài trợ chứng chỉ WSET Level 3 hoặc Certified Sommelier sau 12 tháng, cho đội phục vụ.” None of the six job descriptions offers it.

## Website feedback, 24 Sep 2026: tabs and the booking box

Story and Visit are now the About and Booking tabs (`/about/`, `/booking/`). Their lines in the /story/ and /visit/ tables below moved with them unchanged, and so did the home page's “What Sol is”, three boxes and pull quote (now on `/about/`). The old page titles and the lines listed under “No longer on the site” are gone. New lines:

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| every page | tab: About | — (was “Story / Câu chuyện”) | Giới thiệu |
| every page | tab: Booking | — (was “Visit / Ghé thăm”) | Đặt bàn |
| /about/ | page title: About — Sol, Tây Hồ | Câu chuyện của chúng tôi — Sol, Tây Hồ (the /story/ title, for “Our story — Sol, Tây Hồ”) | Giới thiệu — Sol, Tây Hồ |
| /booking/ | page title: Booking — Sol, Tây Hồ | Ghé thăm và đặt bàn — Sol, Tây Hồ (for “Visit and book — Sol, Tây Hồ”) | Đặt bàn — Sol, Tây Hồ |
| /404 | button: Booking | Ghé thăm (for “Visit”) | Đặt bàn |
| /booking/ | Phone (booking box; replaces the “Email us” and “Call us” buttons) | Gửi email, Gọi điện (the buttons) | Điện thoại |
| /booking/ | Email (booking box) | — | Email |
| /booking/ | Instagram (booking box: @solhanoi; added 26 Sep) | — | Instagram (unchanged) |

No longer on the site (the lines stay in the tables below for the record):

- Home: “Read our story”, the menu preview (“Small plates to share…”, the three sample dishes, the Sangiovese line, “See all food / wine / bar”) and the “Find us in Tây Hồ” band with its hours line. The tabs now lead to those pages.
- /visit/: the “Call us” / “Gọi điện” and “Email us” / “Gửi email” buttons in the booking box (replaced by the Phone and Email lines above).
- The header “Story / Câu chuyện” and “Visit / Ghé thăm” links and the header “Book a table” button (replaced by the tabs).

## Every page

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| every page | screen-reader label: Language | — | Ngôn ngữ |
| every page | screen-reader label: Sol, home | — | Sol, trang chủ |
| every page | screen-reader label: Open navigation | — | Mở menu điều hướng |
| every page | screen-reader label: Main | — | Điều hướng chính |
| every page | screen-reader label: Menu sections | — | Các mục thực đơn |
| every page | screen-reader label: Navigation | — | Điều hướng |
| every page | screen-reader label: Close navigation | — | Đóng menu điều hướng |
| every page | Skip to content | — | Chuyển đến nội dung chính |
| every page | Food | — | Món ăn |
| every page | Pizza, pasta and small plates | — | Pizza, mì Ý và món khai vị |
| every page | 30 wines, 26 by the glass | — | 30 loại vang, 26 loại theo ly |
| every page | Cocktails, beer and sake | — | Cocktail, bia và sake |
| every page | Tuesday to Sunday | Thứ Ba – Chủ Nhật | Thứ Ba đến Chủ Nhật |
| every page | Closed Mondays | — | Nghỉ thứ Hai |
| every page | @solhanoi on Instagram | — | @solhanoi trên Instagram |

## Menu pages

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| menu pages | Tell your server about any allergy before you order. Our kitchen handles wheat, dairy, egg, nuts, shellfish and fish, so we can’t promise any dish is free of them. | Vui lòng báo nhân viên trước khi gọi món. Bếp của chúng tôi sử dụng lúa mì, sữa, trứng, các loại hạt, động vật có vỏ và cá, nên chúng tôi không thể cam kết món ăn hoàn toàn không chứa các thành phần này. | Nếu bạn bị dị ứng với bất kỳ thực phẩm nào, vui lòng báo nhân viên trước khi gọi món. Bếp của chúng tôi sử dụng lúa mì, sữa, trứng, các loại hạt, động vật có vỏ và cá, nên chúng tôi không thể cam kết món ăn hoàn toàn không chứa các thành phần này. |
| menu pages | Photos are welcome — just turn off the flash. | Vui lòng tắt đèn flash trong phòng ăn. | Cứ thoải mái chụp ảnh — chỉ cần tắt đèn flash. |
| menu pages | Children are very welcome. Please keep them at the table — there’s a live fire in the room. | Không chấp nhận trẻ em quấy phá. (for “Misbehaved children will not be tolerated.”) | Trẻ em luôn được chào đón. Vui lòng để các bé ngồi tại bàn — lò củi trong phòng luôn đỏ lửa. |

## /

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| / | page title: Sol — Italian-American restaurant in Tây Hồ, Hanoi | Sol — Ẩm thực Ý–Mỹ tại Tây Hồ, Hà Nội | Sol — Nhà hàng Ý–Mỹ tại Tây Hồ, Hà Nội |
| / | meta description: Wood-fired pizza, pasta made in-house and 26 wines by the glass. Sol opens soon at No 7, Lane 88 Quang An, Tây Hồ, Hanoi. | Sol là nhà hàng Ý–Mỹ sắp khai trương tại Tây Hồ, Hà Nội. (in the source, never shown) | Pizza lò củi, mì Ý làm tại nhà hàng và 26 loại vang theo ly. Sol sắp khai trương tại số 7, ngõ 88 Quảng An, Tây Hồ, Hà Nội. |
| / | with the oven we always wanted | — | cùng chiếc lò chúng tôi luôn mong muốn |
| / | Sol Pizza closed last year. Sol opens on the same stretch of Tây Hồ with more room: a bigger kitchen, a proper bar and a Pavesi wood-fired oven built in Italy. | Sol Pizza đã đóng cửa năm ngoái. Sắp tới, ngay trên con phố ấy ở Tây Hồ, chúng tôi mở lại với nhiều không gian hơn — một căn bếp đúng nghĩa, một quầy bar đúng nghĩa, và chiếc lò chúng tôi luôn mong muốn. | Sol Pizza đã đóng cửa năm ngoái. Sol sẽ mở lại ngay trên con phố ấy ở Tây Hồ, với nhiều không gian hơn: căn bếp rộng hơn, một quầy bar đúng nghĩa và chiếc lò củi Pavesi chế tác tại Ý. |
| / | Lane 88 Quang An, Tây Hồ | Tây Hồ, Hà Nội | Ngõ 88 Quảng An, Tây Hồ |
| / | A neighbourhood restaurant built around pizza. | Một nhà hàng của khu phố, nghiêm túc với món ăn. | Một nhà hàng của khu phố, lấy pizza làm trung tâm. |
| / | Italian-American food began with immigrants: Italian technique, American appetite and whatever the market had that morning. Ours has Đà Lạt spinach and Phú Quốc pepper in it, and imported flour, cheese and tomatoes we won’t compromise on. | Ẩm thực Ý–Mỹ là món ăn của người nhập cư: kỹ thuật Ý, khẩu vị Mỹ, và bất cứ thứ gì chợ địa phương có vào sáng hôm đó. Ở Hà Nội, điều đó nghĩa là rau thơm Việt, hải sản Việt, cùng bột mì, phô mai và cà chua hộp nhập khẩu mà chúng tôi không thỏa hiệp. | Ẩm thực Ý–Mỹ bắt đầu từ những người nhập cư: kỹ thuật Ý, khẩu vị Mỹ và bất cứ thứ gì chợ có vào sáng hôm đó. Món của chúng tôi có rau chân vịt Đà Lạt, tiêu Phú Quốc, cùng bột mì, phô mai và cà chua nhập khẩu — những nguyên liệu chúng tôi không bao giờ thỏa hiệp về chất lượng. |
| / | We’re still building: the oven is in and the team is coming together. Underneath it all is one rule — food quality is non-negotiable. | Chúng tôi vẫn đang hoàn thiện. Lò đã về, bản vẽ đã xong, và đội ngũ đang dần đầy đủ. Mọi thông tin được đánh dấu vàng trên trang này vẫn đang được xác nhận. | Chúng tôi vẫn đang hoàn thiện: lò đã về và đội ngũ đang dần đầy đủ. Nền tảng của tất cả là một nguyên tắc — chất lượng món ăn là điều không thể thỏa hiệp. |
| / | Read our story | Đọc câu chuyện → | Đọc câu chuyện của chúng tôi |
| / | A Pavesi wood-fired oven, built in Italy and shipped to Tây Hồ. Slow-fermented dough, baked fast over real fire. | Lò củi Pavesi, chế tác tại Ý và đưa về Tây Hồ. Bột ủ chậm, rồi ba mươi giây trong lửa thật. | Lò củi Pavesi, chế tác tại Ý và đưa về Tây Hồ. Bột ủ chậm, nướng nhanh trên lửa thật. |
| / | We’d rather cook a short menu well than a long one adequately. | Chúng tôi thà làm mười hai món thật tử tế còn hơn bốn mươi món tàm tạm. | Chúng tôi thà nấu ít món cho thật ngon, còn hơn nhiều món mà tàm tạm. |
| / | Small plates to share, pizza from the wood oven, pasta made in-house, a bar that knows what it’s doing and 26 wines by the glass. | Khai vị để chia sẻ, vài loại pizza, mì tươi làm tại chỗ, hai ba món chính nướng lửa, và tráng miệng. Quầy bar xoay quanh amaro, vermouth và rượu vang Ý. | Món khai vị để chia sẻ, pizza từ lò củi, mì Ý làm tại nhà hàng, một quầy bar biết mình đang làm gì và 26 loại vang theo ly. |
| / | Calabrian chilli, caciocavallo, basil | — | Ớt Calabria, caciocavallo, húng quế |
| / | Ricotta, caramelised onions, parsley | — | Ricotta, hành tây caramel, mùi tây |
| / | Guanciale, tomatoes, pecorino | — | Guanciale, cà chua, pecorino |
| / | See all food | — | Xem tất cả món ăn |
| / | Sangiovese · La Castellina · Tuscany | — | Sangiovese · La Castellina · Toscana |
| / | See all wine | — | Xem tất cả các loại vang |
| / | See all bar | — | Xem tất cả đồ uống |
| / | Find us in Tây Hồ | Tây Hồ, Hà Nội (for “Tây Hồ, Hanoi”) | Tìm chúng tôi ở Tây Hồ |
| / | Tuesday to Sunday, 5pm–11pm. Closed Mondays. | Thứ Ba – Chủ Nhật, 17:00 – 23:00 | Thứ Ba đến Chủ Nhật, 17:00 – 23:00. Nghỉ thứ Hai. |

## /menu/

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| /menu/ | page title: Menu — Sol, Tây Hồ | Thực đơn — Sol, Tây Hồ, Hà Nội | Thực đơn — Sol, Tây Hồ |
| /menu/ | meta description: Pizza from the Pavesi wood oven, pasta made in-house and small plates to start. | Pizza lò củi, mì Ý tươi, món khai vị và quầy bar đầy đủ. Sol, Tây Hồ, Hà Nội. (in the source, never shown) | Pizza từ lò củi Pavesi, mì Ý làm tại nhà hàng và món khai vị để mở đầu. |
| /menu/ | Pizza from the wood oven, pasta made in-house and small plates to start. | Pizza lò củi, mì Ý làm tại nhà hàng, món khai vị để mở đầu, và một quầy bar biết mình đang làm gì. | Pizza từ lò củi, mì Ý làm tại nhà hàng và món khai vị để mở đầu. |
| /menu/ | These are the dishes we cooked at Sol Pizza, and they’re where Sol starts. Expect changes as the new kitchen settles in, and prices here once they’re set. | Đây là thực đơn chúng tôi từng nấu tại Sol Pizza, và là điểm khởi đầu của Sol Hanoi. Các món sẽ còn thay đổi khi căn bếp ổn định và theo mùa của chợ; giá sẽ được đăng khi đã chốt. | Đây là những món chúng tôi từng nấu tại Sol Pizza, và là điểm khởi đầu của Sol. Các món sẽ còn thay đổi khi căn bếp mới đi vào nếp, và giá sẽ được đăng ở đây khi đã chốt. |
| /menu/ | To start, while the oven catches up. | Để mở đầu, trong lúc chờ lò nóng. | Để mở đầu, trong lúc chờ pizza ra lò. |
| /menu/ | Made in-house. | Chỉ phục vụ buổi tối. (for “Dinner only.”) | Làm tại nhà hàng. |

## /menu/wine/

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| /menu/wine/ | page title: Wine list — Sol, Tây Hồ | Danh sách vang — Sol, Tây Hồ, Hà Nội | Danh sách vang — Sol, Tây Hồ |
| /menu/wine/ | meta description: Thirty wines, twenty-six of them by the glass, from Burgundy and Tuscany to Moldova and the Czech Republic. Wine night every Thursday. | Khoảng bốn mươi chai vang từ Ý, Pháp, Tây Ban Nha và xa hơn, phần lớn phục vụ theo ly. Sol, Tây Hồ, Hà Nội. (in the source, never shown) | Ba mươi loại vang, hai mươi sáu loại có theo ly, từ Bourgogne và Toscana đến Moldova và Cộng hòa Séc. Đêm vang vào thứ Năm hằng tuần. |
| /menu/wine/ | Thirty wines, from Burgundy and Tuscany to Moldova and the Czech Republic. Twenty-six of them are open by the glass. | Khoảng bốn mươi chai từ Ý, Pháp, Tây Ban Nha, Đức và xa hơn nữa, phần lớn được phục vụ theo ly. | Ba mươi loại vang, từ Bourgogne và Toscana đến Moldova và Cộng hòa Séc. Hai mươi sáu loại trong số đó có phục vụ theo ly. |
| /menu/wine/ | open by the glass and the bottle | Phục vụ theo ly, ngoài cách bán theo chai. | có theo ly và theo chai |
| /menu/wine/ | This is the Sol Pizza list while the new one is being built. Vintages change and bottles run out, so ask what’s open tonight. | Đây là danh sách như tại Sol Pizza. Niên vụ thay đổi, chai hết hàng, và danh sách của Sol Hanoi vẫn đang được xây dựng — hãy hỏi tối nay có gì. | Đây là danh sách của Sol Pizza trong lúc danh sách mới đang được xây dựng. Niên vụ thay đổi, chai có thể hết, nên hãy hỏi xem tối nay có những chai nào đang mở. |
| /menu/wine/ | 3 wines, 2 by the glass | — | 3 loại vang, 2 loại theo ly |
| /menu/wine/ | glass · house · natural | Theo ly · Vang quán · Tự nhiên (as separate tags) | theo ly · vang quán · tự nhiên |
| /menu/wine/ | glass · house | Theo ly · Vang quán (as separate tags) | theo ly · vang quán |
| /menu/wine/ | 10 wines, 9 by the glass | — | 10 loại vang, 9 loại theo ly |
| /menu/wine/ | 16 wines, 15 by the glass | — | 16 loại vang, 15 loại theo ly |
| /menu/wine/ | glass · natural | Theo ly · Tự nhiên (as separate tags) | theo ly · tự nhiên |
| /menu/wine/ | 1 wine | — | 1 loại vang |
| /menu/wine/ | Wine night | Đêm vang thứ Năm hằng tuần — giảm 50% mọi loại vang theo ly. (one sentence) | Đêm vang |
| /menu/wine/ | every Thursday | Đêm vang thứ Năm hằng tuần — giảm 50% mọi loại vang theo ly. (one sentence) | thứ Năm hằng tuần |
| /menu/wine/ | 50% off every wine by the glass. | Đêm vang thứ Năm hằng tuần — giảm 50% mọi loại vang theo ly. (one sentence) | Giảm 50% mọi loại vang theo ly. |
| /menu/wine/ | Can’t see what you like? | Không có trong danh sách? (for “Not on the list?”) | Chưa thấy chai bạn thích? |

## /menu/bar/

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| /menu/bar/ | page title: Bar — Sol, Tây Hồ | — | Quầy bar — Sol, Tây Hồ |
| /menu/bar/ | meta description: Cocktails, Bia Craft on draft, sake and soft drinks. Happy hour 5–7pm, Tuesday to Sunday. | — | Cocktail, bia tươi Bia Craft, sake và đồ uống không cồn. Happy hour 17:00 – 19:00, từ thứ Ba đến Chủ Nhật. |
| /menu/bar/ | Cocktails, Bia Craft on draft, sake and everything else. It’s a full bar, so ask for anything. | Cocktail, bia tươi Bia Craft, sake và mọi thứ còn lại. | Cocktail, bia tươi Bia Craft, sake và mọi thứ còn lại. Quầy bar đầy đủ, bạn cứ gọi món mình thích. |
| /menu/bar/ | The ones we pour most. | Quầy bar đầy đủ, bạn cứ gọi món mình thích — đây là những ly chúng tôi pha nhiều nhất. | Những ly chúng tôi pha nhiều nhất. |
| /menu/bar/ | From Bia Craft and friends. | — | Từ Bia Craft và những người bạn. |
| /menu/bar/ | Japanese, cold. | — | Sake Nhật, uống lạnh. |
| /menu/bar/ | Everything else. | — | Và mọi thứ còn lại. |
| /menu/bar/ | 5–7pm | Giảm 50% vang quán, sake và bia tươi, 17:00–19:00 mỗi ngày. | 17:00 – 19:00 |
| /menu/bar/ | Tuesday to Sunday: 50% off house wine, sake and draft beer. | Giảm 50% vang quán, sake và bia tươi, 17:00–19:00 mỗi ngày. | Thứ Ba đến Chủ Nhật: giảm 50% vang quán, sake và bia tươi. |

## /story/

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| /story/ | page title: Our story — Sol, Tây Hồ | Câu chuyện — Sol, Tây Hồ, Hà Nội | Câu chuyện của chúng tôi — Sol, Tây Hồ |
| /story/ | meta description: We closed Sol Pizza to build Sol: a bigger kitchen, a proper bar and a Pavesi wood-fired oven on Quang An. | Sol Pizza đã đóng cửa năm ngoái. Sol sắp khai trương tại Tây Hồ, Hà Nội. (in the source, never shown) | Chúng tôi đóng cửa Sol Pizza để xây dựng Sol: căn bếp rộng hơn, một quầy bar đúng nghĩa và lò củi Pavesi trên phố Quảng An. |
| /story/ | We closed Sol Pizza to build Sol. | Đóng lại một chương để mở ra chương khác. | Chúng tôi đóng cửa Sol Pizza để xây dựng Sol. |
| /story/ | We ran Sol Pizza until we could see what it wanted to become — and that the room wouldn’t let it. A small kitchen sets a hard ceiling. So does an oven that’s nearly right. | Chúng tôi mở Sol Pizza ở Tây Hồ và vận hành cho đến khi nhìn thấy rõ nó muốn trở thành điều gì — và rằng không gian đó không cho phép. Một căn bếp nhỏ đặt ra giới hạn cứng. Một chiếc lò gần đúng cũng vậy. | Chúng tôi vận hành Sol Pizza cho đến khi nhìn thấy rõ nó muốn trở thành điều gì — và rằng không gian đó không cho phép. Một căn bếp nhỏ đặt ra giới hạn cứng. Một chiếc lò gần đúng cũng vậy. |
| /story/ | Closing was the harder decision, and the right one. | Đóng cửa là quyết định khó khăn hơn, và là quyết định đúng. [Thêm một câu về ý nghĩa của việc đóng cửa với bạn và đội ngũ.] | Đóng cửa là quyết định khó khăn hơn, và là quyết định đúng. |
| /story/ | The building | Toà nhà mới | Tòa nhà |
| /story/ | Sol takes the first two floors of a building on Quang An — under 200 square metres, small enough to run properly and big enough for what the old place couldn’t do. | Sol chiếm hai tầng đầu của một toà nhà ở Tây Hồ — dưới 200 mét vuông, đủ nhỏ để vận hành chỉn chu và đủ lớn để làm những điều nơi cũ không thể. | Sol chiếm hai tầng đầu của một tòa nhà trên phố Quảng An — dưới 200 mét vuông, đủ nhỏ để vận hành chỉn chu và đủ lớn để làm những điều nơi cũ không thể. |
| /story/ | At its centre is a Pavesi wood-fired oven, built in Italy and shipped to Hanoi. The rest of the kitchen is arranged around it. | Trung tâm của tất cả là chiếc lò củi Pavesi, chế tác tại Ý, đưa về đây và lắp đặt trong mùa hè này. Mọi thứ còn lại trong bếp đều được sắp xếp quanh nó. | Trung tâm của tất cả là chiếc lò củi Pavesi, chế tác tại Ý và đưa về Hà Nội. Mọi thứ còn lại trong bếp đều được sắp xếp quanh nó. |
| /story/ | The team | Căn bếp (for “The kitchen”) | Đội ngũ |
| /story/ | Ngọc runs the kitchen. | Ngọc phụ trách bếp. [Vài dòng về Ngọc — học nghề ở đâu, nấu món gì, vì sao là người phù hợp.] | Ngọc phụ trách bếp. |

## /visit/

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| /visit/ | page title: Visit and book — Sol, Tây Hồ | Ghé thăm & đặt bàn — Sol, Tây Hồ, Hà Nội | Ghé thăm và đặt bàn — Sol, Tây Hồ |
| /visit/ | meta description: No 7, Lane 88 Quang An Street, Tây Hồ, Hanoi. Tuesday to Sunday, 5pm–11pm, from the day we open. Call or email to hold a table. | Địa chỉ, giờ mở cửa và đặt bàn tại Sol, Tây Hồ, Hà Nội. Sắp khai trương. (in the source, never shown) | Số 7, ngõ 88 Quảng An, Tây Hồ, Hà Nội. Thứ Ba đến Chủ Nhật, 17:00 – 23:00, kể từ ngày khai trương. Gọi điện hoặc gửi email để giữ bàn. |
| /visit/ | Sol is on the first two floors of No 7, Lane 88 Quang An. We’re opening soon. | Sol nằm ở hai tầng đầu của một toà nhà tại Tây Hồ. Sắp khai trương. | Sol nằm ở hai tầng đầu của tòa nhà số 7, ngõ 88 Quảng An. Chúng tôi sắp khai trương. |
| /visit/ | Reservations | Đặt bàn | Đặt chỗ |
| /visit/ | Online booking opens closer to the day we open. Until then, call or email us and we’ll hold you a table for opening week. | Đặt bàn trực tuyến sẽ mở gần ngày khai trương. Trong thời gian này, hãy gửi email tới hello@sol.pizza và chúng tôi sẽ giữ bàn cho bạn trong tuần đầu tiên. | Chúng tôi sẽ mở đặt bàn trực tuyến khi gần đến ngày khai trương. Từ nay đến lúc đó, bạn cứ gọi điện hoặc gửi email, chúng tôi sẽ giữ bàn cho bạn trong tuần khai trương. |
| /visit/ | Call us | — | Gọi điện |

## /jobs/

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| /jobs/ | page title: Work with us — Sol, Tây Hồ | Tuyển dụng tại Sol — Tây Hồ, Hà Nội | Tuyển dụng — Sol, Tây Hồ |
| /jobs/ | meta description: We’re hiring a Host and our opening team for the floor and the kitchen. Every application gets a reply. | Sol đang tuyển dụng tại Tây Hồ, Hà Nội trước ngày khai trương: Kế toán nhà hàng và đội ngũ phục vụ, bếp. (in the source, never shown) | Chúng tôi đang tuyển Lễ tân (Host) và đội ngũ khai trương cho khu phục vụ và bếp. Mọi hồ sơ đều được phản hồi. |
| /jobs/ | Front of house · Full time | — | Khu phục vụ · Toàn thời gian |
| /jobs/ | Host | — | Lễ tân (Host) |
| /jobs/ | The first person our guests meet. You’ll welcome them at the door, answer the phone, take online orders and reply to messages. | — | Người đầu tiên khách gặp khi đến Sol. Bạn sẽ đón khách ở cửa, nghe điện thoại, nhận đơn đặt món trực tuyến và trả lời tin nhắn. |
| /jobs/ | 9,000,000–10,000,000 VND gross a month, plus around 2,000,000–4,000,000 VND a month from service charge and tips, paid quarterly. | — | 9.000.000–10.000.000 VND mỗi tháng (lương gross), cộng thêm khoảng 2.000.000–4.000.000 VND mỗi tháng từ phí phục vụ và tiền tip, trả hàng quý. |
| /jobs/ | Apply: email jobs@sol.pizza with “Host” in the subject | — | Ứng tuyển: gửi email tới jobs@sol.pizza, tiêu đề ghi “Host” |
| /jobs/ | Floor and kitchen | — | Phục vụ và bếp |
| /jobs/ | Opening team | Đội ngũ khai trương — phục vụ và bếp (for “Opening team — floor and kitchen”) | Đội ngũ khai trương |
| /jobs/ | September 2026 | Đã tuyển tháng 9 năm 2026 | Tháng 9 năm 2026 |
| /jobs/ | A new home, the same standards. | Một chương mới, cùng một tiêu chuẩn. | Ngôi nhà mới, vẫn những tiêu chuẩn ấy. |
| /jobs/ | Sol is a modern Italian-American restaurant in Tây Hồ, with pizza at its heart, a carefully chosen wine list and a warm, relaxed room. | Đặt tại Tây Hồ, Sol là nhà hàng Mỹ–Ý hiện đại với pizza làm trung tâm, đi cùng danh sách rượu vang được chọn lọc kỹ và không gian ấm áp, thư giãn. | Sol là nhà hàng Ý–Mỹ hiện đại ở Tây Hồ, với pizza làm trung tâm, danh sách vang được chọn lọc kỹ và không gian ấm áp, thư giãn. |
| /jobs/ | This year we start again in a new building, with a refreshed brand and a bigger team — and the belief we started with: food quality is non-negotiable. We’re looking for people who care about good food, real hospitality and doing things properly. | Năm nay Sol bắt đầu một chương mới — một ngôi nhà mới, thương hiệu được làm mới và đội ngũ đang lớn dần — trong khi vẫn tập trung vào điều luôn quan trọng nhất với chúng tôi: món ăn ngon, làm từ nguyên liệu chất lượng cao. / Khi chuẩn bị mở không gian mới, chúng tôi tìm những người quan tâm đến món ăn ngon, lòng hiếu khách chân thành, và làm mọi việc cho tử tế. | Năm nay chúng tôi bắt đầu lại trong một tòa nhà mới, với thương hiệu được làm mới và đội ngũ lớn hơn — cùng niềm tin từ ngày đầu: chất lượng món ăn là điều không thể thỏa hiệp. Chúng tôi tìm những người quan tâm đến món ăn ngon, lòng hiếu khách chân thành và làm mọi việc cho tử tế. |
| /jobs/ | Email your CV to jobs@sol.pizza with the role in the subject line. We read every application within 5 working days and reply to everyone, including the people we can’t take forward. | Gửi CV tới jobs@sol.pizza với tên vị trí ở dòng tiêu đề. Mỗi trang vị trí ghi rõ cần gửi những gì. Chúng tôi xem xét hồ sơ trong 5 ngày làm việc và trả lời mọi ứng viên — kể cả những người chúng tôi không thể tiếp tục. | Gửi CV tới jobs@sol.pizza với tên vị trí ở dòng tiêu đề. Chúng tôi đọc mọi hồ sơ trong vòng 5 ngày làm việc và trả lời tất cả ứng viên, kể cả những bạn chúng tôi chưa thể mời vào vòng tiếp theo. |

## /jobs/restaurant-accountant

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| /jobs/restaurant-accountant | page title: Restaurant Accountant — Sol, Tây Hồ | — (English only) | Kế toán nhà hàng — Sol, Tây Hồ |
| /jobs/restaurant-accountant | meta description: The Restaurant Accountant role at Sol, Tây Hồ, Hanoi. This role has been filled. | — (English only) | Mô tả công việc kế toán nhà hàng tại Sol, Tây Hồ, Hà Nội. Vị trí này đã tuyển xong. |

## /jobs/sous-chef

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| /jobs/sous-chef | page title: Sous Chef — Sol, Tây Hồ | — (English only) | Bếp phó — Sol, Tây Hồ |
| /jobs/sous-chef | meta description: The Sous Chef role at Sol, Tây Hồ, Hanoi. This role has been filled. | — (English only) | Mô tả công việc bếp phó tại Sol, Tây Hồ, Hà Nội. Vị trí này đã tuyển xong. |

## /jobs/restaurant-supervisor

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| /jobs/restaurant-supervisor | page title: Restaurant Supervisor — Sol, Tây Hồ | — (English only) | Giám sát nhà hàng — Sol, Tây Hồ |
| /jobs/restaurant-supervisor | meta description: The Restaurant Supervisor role at Sol, Tây Hồ, Hanoi. This role has been filled. | — (English only) | Mô tả công việc giám sát nhà hàng tại Sol, Tây Hồ, Hà Nội. Vị trí này đã tuyển xong. |

## Role pages

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| role pages | This role has been filled. Thank you to everyone who applied. | Vị trí này đã tuyển xong vào tháng 9 năm 2026. Mô tả được giữ lại để tham khảo. | Vị trí này đã tuyển xong. Cảm ơn tất cả các bạn đã ứng tuyển. |
| role pages | (Vietnamese only: the note above an English-only job description) | Bản mô tả công việc này hiện chỉ có bằng tiếng Anh. Bạn có thể ứng tuyển bằng tiếng Việt hoặc tiếng Anh. | Bản mô tả công việc này chỉ có bằng tiếng Anh. |

## /privacy/

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| /privacy/ | page title: Applicant privacy notice — Sol | — | Thông báo bảo mật dành cho ứng viên — Sol |
| /privacy/ | meta description: How Sol collects, uses and stores personal data from job applicants, under the Law on Personal Data Protection 91/2025/QH15. | — | Cách Sol thu thập, sử dụng và lưu trữ dữ liệu cá nhân của ứng viên, theo Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15. |

## /404

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| /404 | We can’t find that page. | Trang này không có trong thực đơn. (for “That page is not on the menu.”) | Chúng tôi không tìm thấy trang này. |

## Names that now stay as written

The brief says dish, wine and drink names stay as written in both languages. The old site translated these; they now show the English name on the Vietnamese page too. Say if any should go back.

| Page | English | Old VI | New VI |
| --- | --- | --- | --- |
| /menu/ | Marinated olives | Ô liu ướp | Marinated olives (as written) |
| /menu/ | Meatballs with ricotta | Thịt viên với ricotta | Meatballs with ricotta (as written) |
| /menu/ | Bain’s spinach salad | Salad rau chân vịt Bain | Bain’s spinach salad (as written) |
| /menu/ | Caesar salad | Salad Caesar | Caesar salad (as written) |
| /menu/bar/ | Seasonal | Bia theo mùa | Seasonal (as written) |
| /menu/bar/ | House sake | Sake của quán | House sake (as written) |
| /menu/bar/ | Still water | Nước suối | Still water (as written) |
| /menu/bar/ | Sparkling water | Nước có ga | Sparkling water (as written) |
| /menu/bar/ | Lemonade | Nước chanh | Lemonade (as written) |
| /menu/bar/ | Alishan iced tea | Trà đá Alishan | Alishan iced tea (as written) |
| /menu/bar/ | Ginger beer | Bia gừng | Ginger beer (as written) |

## Questions for Linh

1. **Names.** Three Vietnamese reviewers suggested bringing back the old Vietnamese for the generic items in the table above (still water, lemonade, ginger beer, which can read as a beer, marinated olives and so on) and keeping true names (Negroni, Gricia, Dr Pepper, the wines) as written. Say which you prefer.
2. **Service charge.** The menus say “phí dịch vụ” (old text); /jobs/ says “phí phục vụ” (the benefits list, and now the Host pay line). One term site-wide?
3. **Spelling.** Tone marks follow the older style throughout (tòa, thỏa, Cộng hòa); the three “toà” in this build were changed to “tòa” to match.
4. **Role pages.** The three filled job descriptions stay in English, with one Vietnamese line saying so. The six opening-team pages are fully in Vietnamese.
