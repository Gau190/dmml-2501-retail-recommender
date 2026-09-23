# Kế hoạch triển khai BTL Đề 2501 — DMML

## 1. Bối cảnh đề bài
- Đề 2501: "Ứng dụng kỹ thuật khai phá luật kết hợp tích hợp vào hệ thống
  quản lý bán lẻ trên công nghệ .NET để giải quyết bài toán khuyến nghị
  sản phẩm".
- Công nghệ: .NET (ASP.NET Core MVC, .NET 8, SQLite qua EF Core).
- Dữ liệu: Online Retail II (UCI ML Repository) — sẽ tải trực tiếp file
  Excel chính thức.
- Kỹ thuật khai phá: Luật kết hợp (Association Rule Mining) — Apriori và
  FP-Growth (thư viện `mlxtend`), theo đúng công thức Support/Confidence/
  Lift và quy trình 2 giai đoạn dạy trong DMML-LectureNote.03 (tập mục phổ
  biến → sinh luật mạnh).
- Quy trình triển khai dự án DMML (theo LectureNote.01, chuẩn CRISP-DM
  rút gọn): b1 Xác định vấn đề & khám phá dữ liệu → b2 Tiền xử lý dữ liệu
  → b3 Mô hình hoá (khai phá luật) → b4 Đánh giá mô hình → b5 Phân
  phối/tích hợp mô hình vào hệ thống. Báo cáo phải bám sát 5 bước này ở
  chương 2–4.
- Nhóm N21: Vũ Quốc Đạt - 24C1001U5702 (Nhóm trưởng), Đàm Chí Công -
  24C1001U4553, Nguyễn Thị Hồng Nhung - 24C1001U4867, Nguyễn Hoàng Đức -
  24C1001U5759.
- Báo cáo dùng cấu trúc chương giống "Mau bao cao.docx" (Chương 1 Tổng
  quan, Chương 2 Phân tích yêu cầu, Chương 3 Thiết kế, Chương 4 Kết quả
  thực hiện, Chương 5 Kết luận) nhưng nội dung viết lại hoàn toàn cho đề
  tài DMML (không phải ứng dụng quản lý ảnh của mẫu).

## 2. Kiến trúc tổng thể

```
BTL-DMML-2501/
  data-mining/                # Python: khai phá luật kết hợp
    data/raw/                 # dữ liệu gốc tải từ UCI (không commit file lớn)
    data/processed/           # dữ liệu đã làm sạch
    outputs/                  # rules.csv, products.csv, metrics.json, hình vẽ
    src/
      download_data.py        # tải Online Retail II từ UCI
      preprocessing.py        # b2: làm sạch, loại huỷ đơn, gộp giỏ hàng theo Invoice
      mining.py                # b3: Apriori + FP-Growth qua mlxtend
      evaluate.py              # b4: so sánh 2 thuật toán, chọn ngưỡng, đánh giá luật
      export_for_webapp.py     # b5 (phần xuất dữ liệu): ghi rules.csv/products.csv
      run_pipeline.py          # chạy toàn bộ b1→b4 + export, in log từng bước
    requirements.txt
    README.md
  webapp/                      # ASP.NET Core MVC (.NET 8) — b5: tích hợp mô hình
    RetailRecommender.sln
    src/RetailRecommender.Web/
      Models/ (Product, Category, CartItem, Order, OrderItem, AssociationRule)
      Data/ (AppDbContext, DataSeeder đọc products.csv + rules.csv)
      Services/ (IRecommendationService, RecommendationService)
      Controllers/ (Home, Products, Cart, Orders, Admin)
      Views/...
    tests/RetailRecommender.Tests/ (xUnit — test RecommendationService)
  report/
    BaoCao_BTL_DMML_2501.docx
    assets/ (biểu đồ, ảnh chụp màn hình)
  docs/
    PLAN.md (tài liệu này)
```

## 3. Hợp đồng ranh giới (contract) giữa 2 workstream

Đây là phần bắt buộc theo quy trình vì 2 workstream (Python mining và .NET
webapp) chạy song song và giao tiếp qua file, không qua API trực tiếp.

### 3.1 File `data-mining/outputs/products.csv`
Cột bắt buộc, đúng thứ tự, có header, UTF-8, phân cách bằng dấu phẩy:
```
sku,description,unit_price,category
```
- `sku`: string, khớp StockCode gốc trong Online Retail II (đã chuẩn hoá:
  strip khoảng trắng, upper-case).
- `description`: string, tên sản phẩm (lấy Description phổ biến nhất ứng
  với StockCode đó trong dữ liệu).
- `unit_price`: decimal, > 0, làm tròn 2 chữ số (giá trung bình/median
  UnitPrice dương của StockCode đó).
- `category`: string, có thể để "General" nếu không suy ra được (Online
  Retail II không có cột category sẵn, cho phép gán rule-based đơn giản
  hoặc để cố định "General" — không bắt buộc chính xác tuyệt đối).

### 3.2 File `data-mining/outputs/rules.csv`
Cột bắt buộc, đúng thứ tự, có header:
```
antecedent_sku,consequent_sku,support,confidence,lift
```
- Chỉ xuất **luật 1 → 1** (1 antecedent SKU → 1 consequent SKU) để webapp
  tra cứu O(1) theo SKU nguồn — luật nhiều mục vẫn được khai phá và trình
  bày trong báo cáo/`evaluate.py`, nhưng file xuất cho webapp rút gọn về
  dạng 1→1 (nếu luật gốc có |antecedent|>1, KHÔNG đưa vào rules.csv này).
- `antecedent_sku`, `consequent_sku`: phải tồn tại trong `products.csv`
  (webapp sẽ bỏ qua dòng nào vi phạm khi seed, ghi log cảnh báo, không
  throw exception).
- `support`, `confidence`, `lift`: float, `confidence` trong [0,1],
  `lift` > 0.
- Sắp xếp giảm dần theo `confidence` rồi `lift` (giúp webapp không bắt
  buộc phải sort lại, nhưng Service vẫn tự sort để không phụ thuộc thứ tự
  file).
- Ngưỡng lọc cuối cùng (min_support/min_confidence) do `evaluate.py` xác
  định dựa trên phân tích thực nghiệm (số lượng luật sinh ra ở nhiều mức
  ngưỡng), nêu rõ căn cứ chọn trong báo cáo — không hard-code võ đoán.

### 3.3 File `data-mining/outputs/metrics.json`
Dùng để báo cáo viết Chương 4 (không dùng trực tiếp trong webapp), gồm ít
nhất:
```json
{
  "schema_version": 1,
  "generated_at": "<ISO-8601 UTC timestamp>",
  "n_transactions_total_clean": <int>,
  "n_transactions_used_for_mining": <int>,
  "n_unique_skus_total": <int>,
  "n_skus_used_for_mining": <int>,
  "top_n_items_cap": <int>,
  "coverage_pct_after_cap": <float>,
  "min_support": <float>,
  "min_confidence": <float>,
  "apriori": {"n_itemsets": <int>, "runtime_sec": <float>},
  "fpgrowth": {"n_itemsets": <int>, "runtime_sec": <float>},
  "itemsets_equal": <bool>,
  "n_rules_total": <int>,
  "n_rules_1to1_exported": <int>,
  "top_rules_preview": [ {"antecedent_sku":..., "consequent_sku":...,
      "antecedent_desc":..., "consequent_desc":..., "support":...,
      "confidence":..., "lift":...}, ... 10 dòng ... ]
}
```
- `runtime_sec` của mỗi thuật toán: chỉ đo thời gian gọi hàm `apriori()`/
  `fpgrowth()` (không tính I/O đọc CSV/one-hot encode), lấy **giá trị nhỏ
  nhất của 3 lần chạy liên tiếp** trên cùng dữ liệu đã encode sẵn trong bộ
  nhớ (loại nhiễu do máy). Không đo memory (ghi rõ trong báo cáo đây là
  giới hạn đã biết, ngoài phạm vi BTL).
- `itemsets_equal`: kết quả so sánh tập itemsets (làm tròn support 6 chữ
  số thập phân) giữa Apriori và FP-Growth ở cùng min_support — phải là
  `true`; nếu `false` là bug, phải sửa trước khi export.
- Rule cuối cùng dùng để sinh `rules.csv` lấy từ **FP-Growth** (nhanh hơn
  về lý thuyết, phù hợp dữ liệu lớn); Apriori chỉ chạy để đối chiếu/so
  sánh hiệu năng trong báo cáo, không dùng làm nguồn export.

### 3.4 Giới hạn quy mô dữ liệu trước khi khai phá (bắt buộc)
Online Retail II có thể có hàng nghìn SKU khác nhau → ma trận one-hot
(n_transactions × n_unique_skus) có thể quá lớn để chạy Apriori trong thời
gian hợp lý. Quy định bắt buộc trong `mining.py`:
- Hằng số `TOP_N_ITEMS = 300` (có thể chỉnh qua tham số CLI/`config.py`,
  nhưng phải có giá trị mặc định cụ thể, không để "tuỳ ý").
- Trước khi tạo ma trận one-hot, giữ lại giao dịch chỉ gồm các SKU nằm
  trong `TOP_N_ITEMS` sản phẩm bán chạy nhất theo số giao dịch chứa SKU đó
  (loại bỏ phần đuôi dài/long-tail ít có ý nghĩa gợi ý); giao dịch chỉ còn
  0–1 sản phẩm sau khi lọc thì bỏ khỏi tập mining (không đóng góp luật).
- Định nghĩa số liệu tường minh (khớp với schema `metrics.json` mục 3.3):
  - `n_transactions_total_clean` = số Invoice duy nhất **sau** bước làm
    sạch b2 (đã loại đơn huỷ, dòng lỗi, mã không phải sản phẩm) nhưng
    **trước** khi áp `TOP_N_ITEMS`.
  - `n_transactions_used_for_mining` = số Invoice còn lại ≥2 sản phẩm
    **sau** khi áp `TOP_N_ITEMS` — đây mới là số dòng thật đưa vào
    `TransactionEncoder`/Apriori/FP-Growth.
  - `coverage_pct_after_cap = n_transactions_used_for_mining /
    n_transactions_total_clean * 100`.
  - Nêu cả 2 số liệu này trong báo cáo để chứng minh việc giới hạn không
    làm mất tính đại diện của dữ liệu (mục tiêu coverage ≥ 60–70%, nếu
    thấp hơn thì tăng `TOP_N_ITEMS`).
- Đây là bước tiền xử lý được nêu rõ và có căn cứ (giảm chiều dữ liệu),
  không phải cắt xén tuỳ tiện — phù hợp mục 2.3 của đề bài (mô hình phải
  có căn cứ khoa học).

### 3.5 Ownership & failure handling
- Worker Python (mining) sở hữu hoàn toàn `data-mining/`, chỉ ghi vào
  `data-mining/outputs/`, không đụng `webapp/`.
- Worker .NET (webapp) sở hữu hoàn toàn `webapp/`. File CSV mà webapp đọc
  **luôn nằm trong chính project của webapp**, không đọc trực tiếp từ
  `data-mining/outputs/` (tránh vấn đề đường dẫn tương đối/ContentRoot):
  `webapp/src/RetailRecommender.Web/SeedData/products.csv` và
  `.../SeedData/rules.csv`, khai báo trong `.csproj` với
  `CopyToOutputDirectory=PreserveNewest` để luôn có mặt cạnh file chạy
  (`AppContext.BaseDirectory`). Worker .NET tự tạo `products.csv`/
  `rules.csv` **mẫu** (~10 dòng, đúng schema) trong `SeedData/` để dev/test
  độc lập trước khi có dữ liệu thật.
- Sau khi Python pipeline xong, **Claude** (không phải worker) copy đè
  `data-mining/outputs/products.csv` và `rules.csv` thật vào
  `webapp/src/RetailRecommender.Web/SeedData/`, rồi chạy lại webapp để
  seed dữ liệu thật — đây là bước tích hợp thủ công có chủ đích, không
  phải service tự đọc 2 nơi khác nhau.
- **Seed idempotent theo mỗi lần khởi động** (không chỉ "nếu DB rỗng"),
  nhưng **2 bảng dùng 2 chiến lược khác nhau** vì `OrderItem` có khoá
  ngoại (FK) trỏ tới `Product` còn `AssociationRule` thì không bị bảng
  nào tham chiếu:
  - `Product`: **upsert theo `Sku`** — nếu `Sku` đã tồn tại thì cập nhật
    `Description/UnitPrice/Category` tại chỗ (giữ nguyên khoá chính/Id),
    nếu chưa có thì insert mới. **Không bao giờ xoá hàng `Product`** khi
    reseed (kể cả khi SKU đó không còn trong CSV mới) — để không bao giờ
    vi phạm FK với `OrderItem` đã tồn tại từ trước.
  - `AssociationRule`: **không có bảng nào khác tham chiếu tới nó** → an
    toàn để xoá toàn bộ (`RemoveRange` hết bảng) rồi insert lại từ CSV
    mỗi lần start — đơn giản hơn upsert mà không có rủi ro FK.
  - Test bắt buộc: seed lần 1 (sample) → tạo 1 `Order`/`OrderItem` tham
    chiếu 1 `Product` demo (giả lập có đơn hàng thật) → gọi lại
    `DataSeeder` với bộ CSV khác (kể cả bộ CSV không còn chứa SKU đó) →
    xác nhận không exception, `OrderItem`/`Order` cũ vẫn còn nguyên,
    `Product` cũ vẫn còn (không bị xoá), các `Product`/`AssociationRule`
    mới từ CSV vẫn được nạp đúng.
- Export CSV bên Python phải **ghi nguyên tử**: ghi ra file `.tmp` trong
  cùng thư mục rồi `os.replace()` sang tên file cuối — tránh webapp đọc
  phải file đang ghi dở nếu 2 quá trình chạy gần nhau.
- Nếu `rules.csv` rỗng hoặc thiếu khi khởi động: DataSeeder log cảnh báo,
  ứng dụng vẫn chạy được (trang sản phẩm hoạt động, phần khuyến nghị hiển
  thị "Chưa có dữ liệu khuyến nghị") — không crash ứng dụng.
- CSV format bắt buộc: ghi bằng thư viện chuẩn có hỗ trợ quoting đúng
  RFC4180 — Python dùng `csv.writer` (không tự nối chuỗi bằng dấu phẩy),
  .NET đọc bằng `CsvHelper` (không tự `Split(',')`) để description có dấu
  phẩy/dấu ngoặc kép vẫn đúng. Số thực ghi/đọc theo `InvariantCulture`
  (dấu chấm thập phân). File `products.csv`/`rules.csv` không có BOM,
  encoding UTF-8. Cấm luật `antecedent_sku == consequent_sku` ngay tại
  bước export (`export_for_webapp.py` lọc bỏ trước khi ghi), không chỉ
  chặn ở phía service.

## 4. Chi tiết workstream A — Python data-mining pipeline

File/module chính: `data-mining/src/*.py` (liệt kê ở mục 2).

Rủi ro chính:
- Online Retail II là file Excel 2 sheet (Year 2009-2010, Year 2010-2011),
  khá lớn (~1 triệu dòng) → cần đọc bằng `openpyxl`/`pandas.read_excel`,
  có thể chậm; cần cache ra `.parquet`/`.csv` sau bước tải để không phải
  đọc lại Excel mỗi lần chạy.
- Đọc Excel: ép kiểu `Invoice` và `StockCode` về `str` ngay sau khi đọc
  (pandas có thể suy luận nhầm sang numeric với các mã toàn chữ số) trước
  khi làm bất kỳ so sánh/lọc nào.
- Dữ liệu có Invoice bắt đầu bằng "C" là đơn huỷ (cancellation) — phải loại
  bỏ trước khi mining (không được tính vào giỏ hàng).
- Dòng có Quantity <= 0, UnitPrice <= 0, StockCode rỗng/NaN, hoặc
  Description rỗng/NaN → loại bỏ.
- Danh sách mã không phải sản phẩm thật (mã phí/dịch vụ đã biết trong bộ
  Online Retail II, cố định trong code để tái lập được, không tuỳ tiện):
  `{"POST","D","DOT","M","MANUAL","BANK CHARGES","PADS","AMAZONFEE","C2",
  "CRUK","S","ADJUST","ADJUST2","TEST001","TEST002","SAMPLES","GIFT"}`
  cộng thêm mọi StockCode khớp regex `^gift_?0*\d+` với cờ
  `re.IGNORECASE` (mã thẻ quà tặng mệnh giá, ví dụ `gift_0001_10`) — loại
  khỏi tập mining, log số dòng bị loại theo từng lý do.
- Gộp giao dịch: `groupby(["Invoice"])["StockCode"].apply(lambda s:
  sorted(set(s)))` — loại trùng lặp cùng SKU trong 1 invoice trước khi đưa
  vào TransactionEncoder (luật kết hợp chỉ quan tâm sự có mặt, không quan
  tâm số lượng mua).
- Áp dụng giới hạn `TOP_N_ITEMS` theo mục 3.4 **trước** khi tạo ma trận
  one-hot, để tránh bùng nổ bộ nhớ/thời gian chạy trên toàn bộ dữ liệu.
- Chọn `min_support`/`min_confidence` cuối cùng dựa trên bảng thực nghiệm
  ≥3 mức ngưỡng do `evaluate.py` in ra (ví dụ thử min_support ∈
  {0.01, 0.02, 0.05}), không hard-code một giá trị duy nhất mà không có
  số liệu đối chiếu.

Test case cụ thể (Claude sẽ tự QC lại, worker phải tự chạy qua trước khi
báo xong):
1. `download_data.py` chạy xong → tồn tại file raw trong
   `data-mining/data/raw/` với kích thước > 0.
2. `preprocessing.py` → DataFrame kết quả không còn Invoice bắt đầu "C",
   không còn Quantity<=0 hoặc UnitPrice<=0; số giao dịch (invoice) duy
   nhất được in ra log và khớp `metrics.json.n_transactions_total_clean`.
3. `mining.py` chạy Apriori và FP-Growth trên cùng tập giao dịch đã encode
   sẵn (cùng biến DataFrame one-hot trong bộ nhớ), cùng min_support → tập
   frequent itemsets giống nhau (so sánh tập `frozenset(items)`, support
   làm tròn 6 chữ số thập phân phải bằng nhau) → gán `itemsets_equal` vào
   metrics.json; nếu `False` phải dừng lại sửa bug trước khi export, không
   được export luật khi 2 thuật toán lệch nhau. Đo `runtime_sec` riêng cho
   từng thuật toán theo đúng mục 3.3 (min của 3 lần chạy, không tính I/O).
4. `evaluate.py` in ra bảng số lượng luật theo >= 3 mức min_support/
   min_confidence khác nhau để chọn ngưỡng cuối, có log rõ ngưỡng được
   chọn và lý do (ví dụ: số luật không quá ít cũng không quá nhiều, ví dụ
   50–300 luật).
5. `export_for_webapp.py` → `products.csv` và `rules.csv` đúng schema mục
   3.1/3.2, không có dòng trùng `antecedent_sku,consequent_sku`, mọi
   SKU trong rules.csv tồn tại trong products.csv.
6. `run_pipeline.py` chạy toàn bộ b1→b4+export bằng 1 lệnh, in log theo
   từng bước, kết thúc bằng dòng tổng kết số liệu chính (giống nội dung
   `metrics.json`).

## 5. Chi tiết workstream B — ASP.NET Core webapp

File/module chính: `webapp/src/RetailRecommender.Web/*`.

Chức năng bắt buộc:
- Danh mục sản phẩm (Products: list + detail) — dữ liệu từ `products.csv`
  qua DataSeeder lúc khởi động (upsert theo Sku mỗi lần start, xem mục
  3.5 — không phải chỉ chạy khi DB rỗng).
- Trang chi tiết sản phẩm hiển thị khối "Khách hàng cũng mua" — gọi
  `IRecommendationService.GetRecommendationsForProduct(sku, topN=4)`, lấy
  từ bảng AssociationRule (seed từ rules.csv), sắp xếp theo confidence rồi
  lift giảm dần.
- Giỏ hàng (Cart, lưu qua ASP.NET Core Session — KHÔNG cần đăng nhập
  user thật, đúng phạm vi học phần) — trang giỏ hàng hiển thị khối gợi ý
  tổng hợp từ tất cả SKU đang có trong giỏ (`GetRecommendationsForCart`),
  loại trừ SKU đã có sẵn trong giỏ. **Thuật toán gộp (chốt cứng, không để
  worker tự chọn):** gom mọi luật có `AntecedentSku` thuộc giỏ hàng và
  `ConsequentSku` không thuộc giỏ hàng; nếu cùng 1 `ConsequentSku` được
  nhiều SKU trong giỏ cùng gợi ý, lấy `confidence` **lớn nhất** trong số
  đó làm điểm chính, `lift` của đúng luật đã chọn làm tiêu chí phụ; sắp
  xếp giảm dần theo `(confidence, lift)`, tie-break cuối cùng theo
  `ConsequentSku` tăng dần (đảm bảo kết quả xác định, không phụ thuộc thứ
  tự duyệt); lấy tối đa `topN` (mặc định 6).
- Checkout đơn giản tạo Order + OrderItem (không cần thanh toán thật).
- Trang Admin xem danh sách luật kết hợp đã khai phá (đọc từ
  AssociationRule) — chứng minh mô hình đã được tích hợp, không chỉ ẩn
  trong code.

Rủi ro chính & quyết định chốt cứng (worker không tự chọn khác):
- EF Core + SQLite dùng `EnsureCreated()` (KHÔNG dùng migrations) — chỉ
  cần NuGet `Microsoft.EntityFrameworkCore.Sqlite` (8.x), không cần
  `Microsoft.EntityFrameworkCore.Design` hay `dotnet-ef`. Ghi rõ trong
  README đây là lựa chọn phù hợp phạm vi BTL, không phải production.
- Đọc CSV dùng NuGet `CsvHelper` (bản mới nhất tương thích `net8.0`) —
  kiểm tra `dotnet restore` thành công trước khi coi là chốt xong; nếu
  không tải được NuGet (không có mạng) thì báo lại cho Claude thay vì tự
  ý viết parser tay.
- Giỏ hàng dùng Session: cần cấu hình trong `Program.cs`:
  `builder.Services.AddDistributedMemoryCache()`,
  `builder.Services.AddSession(...)`, và `app.UseSession()` (đặt trước
  `app.UseAuthorization()`/routing endpoints) — đây là middleware có sẵn
  trong shared framework ASP.NET Core, không cần thêm NuGet riêng.
- `RecommendationService` phải là 1 class dễ unit-test (nhận
  `AppDbContext` dùng EF Core InMemory provider trong test, hoặc nhận
  `IEnumerable<AssociationRule>` trực tiếp — chọn cách nào cũng được,
  miễn test không cần SQLite thật).
- Unique keys bắt buộc trong `OnModelCreating`: `Product.Sku` unique index,
  `AssociationRule` unique index trên `(AntecedentSku, ConsequentSku)`.

Test case cụ thể:
1. `dotnet build` toàn bộ solution thành công, không warning-as-error mới.
2. `dotnet test` (xUnit) pass — tối thiểu các case:
   - `GetRecommendationsForProduct("X")` trả đúng thứ tự giảm dần theo
     confidence khi có nhiều luật cùng antecedent.
   - `GetRecommendationsForProduct` loại trừ chính SKU đang xem khỏi kết
     quả (đề phòng luật lỗi A→A, dù export đã lọc, service vẫn phòng thủ).
   - `GetRecommendationsForCart([A,B])` không trả lại A hoặc B trong kết
     quả dù luật A→B hoặc B→A tồn tại; đúng quy tắc gộp max(confidence)
     nêu ở mục 5 khi 2 SKU trong giỏ cùng gợi ý 1 consequent.
   - `GetRecommendationsForProduct` với SKU không có luật nào → trả về
     danh sách rỗng, không throw.
   - CSV importer: parse đúng dòng có `description` chứa dấu phẩy/dấu
     ngoặc kép (ví dụ `"CERAMIC, HEART SHAPE MUG"`), parse đúng số thực
     dạng `InvariantCulture` (`"3.75"`), bỏ qua (không throw) dòng
     `rules.csv` có SKU không tồn tại trong `products.csv` hoặc dòng
     duplicate `(AntecedentSku, ConsequentSku)`.
   - Reseed lần 2: seed bằng `products.sample.csv`/`rules.sample.csv`, sau
     đó thay bằng file khác rồi khởi động lại `DataSeeder` (gọi trực tiếp
     trong test, không cần restart process thật) → `AssociationRule` phản
     ánh đúng bộ file mới (bảng cũ bị xoá sạch trước khi nạp lại); `Product`
     được upsert theo Sku (SKU trùng thì cập nhật thông tin mới, SKU cũ
     không còn trong file mới vẫn giữ nguyên trong DB, không bị xoá).
   - Reseed khi đã có `OrderItem` tham chiếu tới 1 `Product`: gọi lại
     `DataSeeder` (kể cả với CSV không còn chứa SKU đó) → không throw FK
     exception, `Order`/`OrderItem`/`Product` liên quan vẫn còn nguyên.
3. Chạy `dotnet run` thật (Claude tự chạy, không chỉ tin worker) → mở
   trang chủ, trang chi tiết 1 sản phẩm có luật mẫu → thấy khối khuyến
   nghị hiển thị đúng sản phẩm mong đợi theo `rules.sample.csv`; thêm sản
   phẩm vào giỏ, mở trang giỏ hàng, xác nhận khối gợi ý tổng hợp đúng.

## 6. Phân loại theo 2 trục

- `EXECUTION_COMPLEXITY`: MULTI_WORKSTREAM — 2 workstream độc lập file
  (data-mining vs webapp), chạy song song qua Codex CLI 2 instance.
- `ASSURANCE_RISK`: MEDIUM — không có dữ liệu người dùng thật, không
  production, nhưng cần đúng logic nghiệp vụ (schema contract, kết quả
  mining đúng) và phải build/test/chạy thật được → QC trực tiếp
  file:line + chạy build/test/run thật cho cả 2 workstream, KHÔNG cần
  thêm 1 reviewer CLI độc lập thứ 3 (không chạm auth/bảo mật/concurrency
  sản xuất).

## 7. Kế hoạch báo cáo (sau khi 2 workstream xong)
Cấu trúc theo mẫu file "Mau bao cao.docx" (5 chương), nội dung viết lại
hoàn toàn cho đề DMML:
- Ch.1 Tổng quan: giới thiệu đề tài, mục tiêu, quy trình DMML 5 bước,
  phân công nhiệm vụ theo nhóm N21, công nghệ dùng.
- Ch.2 Phân tích yêu cầu: mô tả bài toán khuyến nghị sản phẩm, yêu cầu
  chức năng hệ thống bán lẻ + yêu cầu về mô hình (support/confidence/lift,
  ngưỡng), yêu cầu phi chức năng.
- Ch.3 Thiết kế: kiến trúc tổng thể (data-mining → export → webapp),
  thiết kế dữ liệu (ERD Product/Order/AssociationRule), thiết kế xử lý
  (pipeline Apriori/FP-Growth), thiết kế màn hình.
- Ch.4 Kết quả thực hiện: số liệu thực tế từ `metrics.json`, bảng so sánh
  Apriori vs FP-Growth, các luật kết hợp tiêu biểu tìm được, ảnh chụp màn
  hình webapp thật (Claude tự chạy app và chụp), kiểm thử.
- Ch.5 Kết luận: đánh giá so mục tiêu, hạn chế, hướng phát triển.
- Tài liệu tham khảo: Agrawal & Srikant 1994, Han et al. FP-Growth 2000,
  Online Retail II UCI, lecture note DMML.

## 8. Trình tự thực hiện
1. (Claude) Gửi kế hoạch này cho Codex (read-only) để phản biện → sửa tới
   khi Codex xác nhận READY-TO-DISPATCH.
2. (Claude) Tạo file mẫu `products.sample.csv`/`rules.sample.csv` +
   `requirements.txt` khung trước khi dispatch để 2 worker có thể chạy
   song song ngay từ đầu.
3. Dispatch song song 2 Codex worker (workspace-write), mỗi worker chỉ
   đụng thư mục của mình.
4. Claude QC từng workstream: đọc diff, chạy `run_pipeline.py` thật với
   dữ liệu UCI thật, chạy `dotnet build && dotnet test`, chạy
   `dotnet run` thật và kiểm tra trên trình duyệt/curl.
5. Tích hợp: Claude copy `data-mining/outputs/products.csv` và
   `rules.csv` thật đè vào `webapp/src/RetailRecommender.Web/SeedData/`,
   chạy lại webapp (seed tự động upsert Product theo Sku và nạp lại toàn
   bộ AssociationRule mỗi lần start theo mục 3.5), xác nhận khuyến nghị
   hiển thị đúng dữ liệu thật.
6. Commit git sau mỗi lần QC pass.
7. Viết báo cáo Word theo cấu trúc mục 7, dùng số liệu/ảnh chụp thật.
