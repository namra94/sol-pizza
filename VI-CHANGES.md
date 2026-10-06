# Vietnamese changes for review — Printed menu build

For Linh. Every Vietnamese line this build adds or changes, page by page: page · English · old VI · new VI. 111 lines, plus 11 dish and drink names that now stay as written. Anything not listed here is the Vietnamese the site already had.

- **Old VI** is what the live site said before this build. “—” means there was no Vietnamese (a new line, or the old site showed English only). Where the English line itself changed, the old English is noted in brackets.
- Lines marked “in the source, never shown” were written in the old generator but never reached a page.
- To change a line, edit it in `build/gen.py` (or `build/menu-data.json` for the menu), in the `t('English', 'Tiếng Việt')` pair, and rebuild.
- Not listed: typographic-only changes (straight to curly quotes, dash spacing), and the applicant privacy notice, whose text is unchanged.

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
