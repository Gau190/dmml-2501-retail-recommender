<!--
Bản nháp nội dung báo cáo BTL Đề 2501 - DMML. Cấu trúc chương bám theo
"Mau bao cao.docx" (mẫu Khoa CNTT). Các đoạn có [[SỐ LIỆU THẬT]] sẽ được
điền lại bằng số liệu/ảnh chụp thật sau khi QC xong 2 workstream.
-->

# TRƯỜNG ĐẠI HỌC MỞ HÀ NỘI — KHOA CÔNG NGHỆ THÔNG TIN

# BÀI TẬP LỚN
# NHẬP MÔN KHAI PHÁ DỮ LIỆU VÀ MÁY HỌC

## ĐỀ SỐ 2501
### Ứng dụng kỹ thuật khai phá luật kết hợp tích hợp vào hệ thống quản lý bán lẻ trên công nghệ .NET để giải quyết bài toán khuyến nghị sản phẩm

Nhóm N21
Sinh viên thực hiện:
- Vũ Quốc Đạt - 24C1001U5702 (Nhóm trưởng)
- Đàm Chí Công - 24C1001U4553
- Nguyễn Thị Hồng Nhung - 24C1001U4867
- Nguyễn Hoàng Đức - 24C1001U5759

Hà Nội, năm 2026

---

# CHƯƠNG 1. TỔNG QUAN VỀ ĐỀ TÀI

## 1.1 Giới thiệu đề tài
Trong lĩnh vực bán lẻ, một trong những nhu cầu phổ biến nhất là gợi ý cho
khách hàng những sản phẩm có khả năng họ sẽ mua thêm, dựa trên hành vi
mua sắm của những khách hàng khác có giỏ hàng tương tự — kỹ thuật này
thường được biết đến dưới tên gọi "khách hàng cũng mua" hoặc "thường
được mua cùng nhau". Đề tài xây dựng một hệ thống quản lý bán lẻ trên nền
tảng ASP.NET Core (.NET 8), trong đó chức năng khuyến nghị sản phẩm được
tích hợp dựa trên kết quả khai phá luật kết hợp (Association Rule Mining)
từ dữ liệu giao dịch bán lẻ thực tế Online Retail II (UCI ML Repository).

## 1.2 Đánh giá các đề tài liên quan
Các hệ thống thương mại điện tử lớn (Amazon, Shopee...) đều có chức năng
gợi ý sản phẩm dựa trên nhiều kỹ thuật khác nhau (collaborative filtering,
content-based, association rules...). Trong phạm vi học phần Nhập môn
Khai phá dữ liệu và Máy học, đề tài lựa chọn tập trung đúng vào kỹ thuật
đã học — khai phá luật kết hợp bằng thuật toán Apriori và FP-Growth — để
đảm bảo minh hoạ rõ ràng toàn bộ quy trình DMML từ dữ liệu thô đến mô hình
tích hợp trong hệ thống thật, thay vì dàn trải nhiều kỹ thuật.

## 1.3 Mục đích của đề tài
Hiện thực đầy đủ quy trình triển khai một dự án DMML (theo đề cương học
phần): xác định vấn đề, tiền xử lý dữ liệu, khai phá mô hình (luật kết
hợp), đánh giá mô hình dựa trên các độ đo khoa học (support, confidence,
lift), và tích hợp mô hình vào một hệ thống ứng dụng cụ thể để chứng minh
giá trị thực tiễn — đúng theo yêu cầu 2.3–2.4 của đề bài.

## 1.4 Mục tiêu của đề tài
- Thu thập và tiền xử lý dữ liệu giao dịch bán lẻ Online Retail II.
- Khai phá luật kết hợp bằng 2 thuật toán Apriori và FP-Growth, so sánh
  hiệu năng và xác nhận tính đúng đắn (2 thuật toán phải cho cùng kết quả
  tập mục phổ biến).
- Đánh giá và lựa chọn ngưỡng support/confidence có căn cứ thực nghiệm.
- Xây dựng hệ thống quản lý bán lẻ tối thiểu (danh mục sản phẩm, giỏ
  hàng, đặt hàng) trên ASP.NET Core MVC (.NET 8) + SQLite.
- Tích hợp mô hình luật kết hợp vào chức năng khuyến nghị sản phẩm ở 2
  điểm chạm chính: trang chi tiết sản phẩm ("Khách hàng cũng mua") và
  trang giỏ hàng (gợi ý tổng hợp theo toàn bộ giỏ).

## 1.5 Quy trình thực hiện

### 1.5.1 Quy trình triển khai dự án DMML
Đề tài bám sát quy trình 5 bước được giảng dạy trong học phần (tương
đương chuẩn CRISP-DM rút gọn):

| Bước | Nội dung | Công cụ/Kết quả |
|---|---|---|
| b1. Xác định vấn đề & khám phá dữ liệu | Xác định bài toán khuyến nghị sản phẩm, khảo sát dữ liệu Online Retail II | Python, pandas |
| b2. Tiền xử lý dữ liệu | Làm sạch đơn hàng huỷ, dữ liệu lỗi, mã không phải sản phẩm, gộp giao dịch theo hoá đơn | pandas |
| b3. Mô hình hoá (khai phá luật) | Áp dụng Apriori và FP-Growth qua mlxtend | mlxtend |
| b4. Đánh giá mô hình | So sánh 2 thuật toán, chọn ngưỡng support/confidence dựa trên thực nghiệm | pandas, matplotlib |
| b5. Phân phối/tích hợp mô hình | Xuất luật kết hợp, tích hợp vào webapp ASP.NET Core | ASP.NET Core, EF Core, SQLite |

## 1.6 Phân công nhiệm vụ

| Họ và tên | MSSV | Nhiệm vụ | Tỷ lệ đóng góp |
|---|---|---|---|
| Vũ Quốc Đạt (Nhóm trưởng) | 24C1001U5702 | Điều phối chung; thiết kế kiến trúc hệ thống; phát triển webapp ASP.NET Core (Controllers, Services khuyến nghị); tích hợp dữ liệu luật kết hợp | 25% |
| Đàm Chí Công | 24C1001U4553 | Xây dựng pipeline khai phá dữ liệu Python (tiền xử lý, Apriori/FP-Growth, đánh giá, export); tổng hợp và biên soạn báo cáo | 25% |
| Nguyễn Thị Hồng Nhung | 24C1001U4867 | Phân tích yêu cầu; thiết kế dữ liệu (ERD); thiết kế màn hình; kiểm thử chức năng webapp | 25% |
| Nguyễn Hoàng Đức | 24C1001U5759 | Đánh giá mô hình (so sánh Apriori/FP-Growth, lựa chọn ngưỡng); kiểm thử pipeline dữ liệu; hỗ trợ viết tài liệu tham khảo | 25% |

## 1.7 Kế hoạch thực hiện

| Giai đoạn | Sản phẩm |
|---|---|
| Tuần 1 | Phân tích đề bài, khảo sát dữ liệu Online Retail II, thiết kế kiến trúc |
| Tuần 2 | Tiền xử lý dữ liệu, khai phá luật kết hợp (Apriori/FP-Growth), đánh giá mô hình |
| Tuần 3 | Xây dựng webapp ASP.NET Core, tích hợp mô hình vào chức năng khuyến nghị |
| Tuần 4 | Kiểm thử tổng thể, hoàn thiện báo cáo |

## 1.8 Công nghệ dự kiến sử dụng
- **Khai phá dữ liệu:** Python 3.13, pandas, mlxtend (Apriori, FP-Growth,
  TransactionEncoder, association_rules), matplotlib.
- **Ứng dụng web:** ASP.NET Core MVC (.NET 8), Entity Framework Core +
  SQLite, CsvHelper, ASP.NET Core Session (giỏ hàng).
- **Kiểm thử:** xUnit + EF Core InMemory provider.
- **Dữ liệu:** Online Retail II (UCI Machine Learning Repository, id 502).

---

# CHƯƠNG 2. PHÂN TÍCH YÊU CẦU

## 2.1 Quy trình nghiệp vụ
- **P01 Xem danh mục và chi tiết sản phẩm:** Khách hàng duyệt danh sách
  sản phẩm, xem chi tiết 1 sản phẩm kèm khối gợi ý "Khách hàng cũng mua".
- **P02 Quản lý giỏ hàng:** Khách hàng thêm/xoá sản phẩm khỏi giỏ hàng;
  hệ thống hiển thị khối gợi ý tổng hợp dựa trên toàn bộ sản phẩm trong
  giỏ.
- **P03 Đặt hàng:** Khách hàng tạo đơn hàng từ giỏ hàng hiện tại.
- **P04 Quản trị luật kết hợp:** Quản trị viên xem danh sách luật kết hợp
  đã khai phá được tích hợp trong hệ thống.

## 2.2 Yêu cầu chức năng

### 2.2.1 Xem danh sách/chi tiết sản phẩm (FR01)
| Thuộc tính | Mô tả |
|---|---|
| Mô tả | Hiển thị danh mục và chi tiết sản phẩm |
| Tác nhân | Khách hàng |
| Dữ liệu vào | SKU sản phẩm |
| Kết quả đầu ra | Thông tin sản phẩm + tối đa 4 sản phẩm khuyến nghị liên quan (sắp xếp theo Confidence, Lift giảm dần) |
| Liên kết nghiệp vụ | P01 |

### 2.2.2 Khuyến nghị theo giỏ hàng (FR02)
| Thuộc tính | Mô tả |
|---|---|
| Mô tả | Gợi ý sản phẩm bổ sung dựa trên toàn bộ giỏ hàng |
| Tác nhân | Khách hàng |
| Dữ liệu vào | Danh sách SKU đang có trong giỏ |
| Kết quả đầu ra | Tối đa 6 sản phẩm gợi ý, không trùng sản phẩm đã có trong giỏ, xếp hạng theo confidence lớn nhất rồi lift |
| Liên kết nghiệp vụ | P02 |

### 2.2.3 Thêm/xoá sản phẩm khỏi giỏ hàng (FR03)
| Thuộc tính | Mô tả |
|---|---|
| Mô tả | Quản lý giỏ hàng qua Session |
| Tác nhân | Khách hàng |
| Dữ liệu vào | SKU, số lượng |
| Kết quả đầu ra | Giỏ hàng được cập nhật, hiển thị lại tổng tiền |
| Liên kết nghiệp vụ | P02 |

### 2.2.4 Đặt hàng (FR04)
| Thuộc tính | Mô tả |
|---|---|
| Mô tả | Tạo đơn hàng từ giỏ hàng |
| Tác nhân | Khách hàng |
| Dữ liệu vào | Giỏ hàng hiện tại |
| Kết quả đầu ra | 1 bản ghi Order + các OrderItem tương ứng, giỏ hàng được xoá |
| Liên kết nghiệp vụ | P03 |

### 2.2.5 Xem danh sách luật kết hợp (FR05)
| Thuộc tính | Mô tả |
|---|---|
| Mô tả | Quản trị viên xem toàn bộ luật kết hợp đã tích hợp |
| Tác nhân | Quản trị viên |
| Dữ liệu vào | (không có) |
| Kết quả đầu ra | Bảng luật kết hợp gồm antecedent, consequent, support, confidence, lift |
| Liên kết nghiệp vụ | P04 |

## 2.3 Yêu cầu về mô hình khai phá dữ liệu
| Mã | Yêu cầu |
|---|---|
| MR01 | Mô hình phải được huấn luyện/khai phá trên dữ liệu giao dịch thật, có nguồn gốc rõ ràng (Online Retail II, UCI) |
| MR02 | Luật kết hợp được chọn phải thoả ngưỡng min_support và min_confidence xác định qua thực nghiệm, có căn cứ khoa học (không tuỳ ý) |
| MR03 | Kết quả khai phá phải được xác nhận đúng đắn bằng cách đối chiếu 2 thuật toán độc lập (Apriori và FP-Growth) cho cùng 1 tập mục phổ biến |
| MR04 | Cấm sinh luật A→A (một sản phẩm "khuyến nghị" chính nó) |

## 2.4 Yêu cầu phi chức năng
| Mã | Yêu cầu |
|---|---|
| NFR01 | Ứng dụng khởi động và tự nạp dữ liệu sản phẩm/luật kết hợp mà không cần thao tác thủ công (DataSeeder tự động) |
| NFR02 | Khi dữ liệu luật kết hợp trống hoặc thiếu, hệ thống vẫn hoạt động bình thường (không crash), chỉ ẩn khối khuyến nghị |
| NFR03 | Giỏ hàng của khách hàng không bị mất khi hệ thống khởi động lại nạp dữ liệu catalog mới (dữ liệu Order/giỏ hàng tách biệt khỏi dữ liệu suy ra từ mô hình) |
| NFR04 | Toàn bộ pipeline khai phá dữ liệu chạy lại được bằng 1 lệnh duy nhất, có log rõ ràng từng bước để tái lập kết quả |

---

# CHƯƠNG 3. THIẾT KẾ CÁC CHỨC NĂNG

## 3.1 Kiến trúc tổng thể
Hệ thống gồm 2 thành phần chính giao tiếp qua file dữ liệu trung gian
(không qua API trực tiếp):

```
[Online Retail II - UCI]
        |
        v
[Python: data-mining pipeline]  --(b1 → b4: tiền xử lý, Apriori/FP-Growth, đánh giá)-->
        |
        v  (export: products.csv, rules.csv, metrics.json)
        |
[ASP.NET Core webapp: SeedData/]  --(DataSeeder: upsert Product, reload AssociationRule)-->
        |
        v
[SQLite database]
        |
        v
[RecommendationService] --> [Controllers/Views: Products, Cart, Orders, Admin]
```

Việc tách 2 thành phần qua file CSV trung gian (thay vì gọi trực tiếp
Python từ .NET) giúp mô hình có thể huấn luyện lại độc lập, dễ kiểm soát
phiên bản dữ liệu, và đúng với thực tế triển khai MLOps đơn giản (batch
export mô hình, hệ thống ứng dụng chỉ tiêu thụ kết quả).

## 3.2 Thiết kế dữ liệu

### 3.2.1 Sơ đồ thực thể (ERD, mô tả dạng văn bản)
- `Product (Id, Sku[unique], Description, UnitPrice, Category)`
- `AssociationRule (Id, AntecedentSku, ConsequentSku, Support, Confidence,
  Lift)` — unique index (AntecedentSku, ConsequentSku)
- `Order (Id, CreatedAt)` 1 — n `OrderItem (Id, OrderId[FK], ProductId[FK],
  Quantity, UnitPriceAtOrder)`

### 3.2.2 Hợp đồng dữ liệu giữa pipeline và webapp
| File | Cột | Vai trò |
|---|---|---|
| `products.csv` | sku, description, unit_price, category | Nguồn nạp bảng Product |
| `rules.csv` | antecedent_sku, consequent_sku, support, confidence, lift | Nguồn nạp bảng AssociationRule (chỉ luật 1→1) |
| `metrics.json` | (xem Chương 4) | Số liệu phục vụ báo cáo, không nạp vào webapp |

## 3.3 Thiết kế xử lý — pipeline khai phá luật kết hợp
1. **Tiền xử lý:** loại đơn hàng huỷ (Invoice bắt đầu "C"), loại dòng dữ
   liệu lỗi (Quantity/UnitPrice không dương, SKU/Description rỗng), loại
   các mã không phải sản phẩm thật (phí vận chuyển, phí ngân hàng, thẻ
   quà tặng...), gộp mỗi hoá đơn (Invoice) thành 1 giao dịch chứa tập SKU
   duy nhất.
2. **Giới hạn quy mô:** giữ lại 300 sản phẩm bán chạy nhất (TOP_N_ITEMS)
   trước khi mã hoá one-hot, nhằm đảm bảo thời gian chạy hợp lý mà vẫn
   giữ phần lớn giao dịch có ý nghĩa (xem số liệu coverage ở Chương 4).
3. **Khai phá:** áp dụng song song Apriori và FP-Growth (thư viện
   mlxtend) trên cùng ma trận giao dịch, đối chiếu kết quả tập mục phổ
   biến phải trùng khớp — xác nhận tính đúng đắn của cài đặt.
4. **Sinh luật:** từ tập mục phổ biến (dùng kết quả FP-Growth), sinh luật
   kết hợp theo hàm `association_rules` với ngưỡng min_confidence đã
   chọn, rút gọn về luật 1→1 để phục vụ tra cứu O(1) theo SKU trong
   webapp.
5. **Xuất dữ liệu:** ghi `products.csv`, `rules.csv`, `metrics.json` theo
   đúng hợp đồng dữ liệu (mục 3.2.2), ghi nguyên tử để tránh đọc file dở.

## 3.4 Thiết kế xử lý — chức năng khuyến nghị trong webapp
- **Trang chi tiết sản phẩm:** truy vấn `AssociationRule` theo
  `AntecedentSku = sku hiện tại`, loại trừ chính nó, sắp xếp giảm dần theo
  (Confidence, Lift), lấy top 4.
- **Trang giỏ hàng:** với mỗi SKU trong giỏ, truy vấn luật có
  `AntecedentSku` thuộc giỏ; gộp theo `ConsequentSku`, chọn Confidence lớn
  nhất trong các luật trùng consequent làm điểm chính, Lift của đúng luật
  đó làm tiêu chí phụ; loại các SKU đã có trong giỏ; sắp xếp và lấy top 6.
- **Nạp dữ liệu (DataSeeder):** chạy mỗi lần khởi động ứng dụng — bảng
  `Product` được upsert theo `Sku` (không bao giờ xoá, tránh vỡ khoá
  ngoại với `OrderItem`), bảng `AssociationRule` được nạp lại toàn bộ từ
  CSV (an toàn vì không có bảng nào tham chiếu tới nó).

## 3.5 Thiết kế màn hình
- Trang chủ: danh mục sản phẩm dạng lưới.
- Trang chi tiết sản phẩm: thông tin sản phẩm + khối "Khách hàng cũng
  mua" (tối đa 4 sản phẩm) + nút "Thêm vào giỏ".
- Trang giỏ hàng: danh sách sản phẩm trong giỏ, tổng tiền, khối "Có thể
  bạn cũng thích" (gợi ý tổng hợp, tối đa 6 sản phẩm), nút "Đặt hàng".
- Trang quản trị luật kết hợp: bảng liệt kê toàn bộ luật (antecedent,
  consequent, support, confidence, lift).

[[ẢNH CHỤP MÀN HÌNH THẬT SẼ ĐƯỢC CHÈN Ở CHƯƠNG 4]]

---

# CHƯƠNG 4. KẾT QUẢ THỰC HIỆN

*(Chương này sẽ được điền số liệu, bảng so sánh, và ảnh chụp màn hình
thật sau khi 2 workstream hoàn tất QC — hiện đang chờ kết quả chạy pipeline
thật trên dữ liệu Online Retail II và webapp thật.)*

## 4.1 Kết quả tiền xử lý dữ liệu
[[SỐ LIỆU THẬT: n_transactions_total_clean, n_unique_skus_total, tỷ lệ
dòng bị loại theo từng lý do]]

## 4.2 Kết quả khai phá luật kết hợp
[[SỐ LIỆU THẬT: TOP_N_ITEMS, coverage_pct_after_cap,
n_transactions_used_for_mining, min_support/min_confidence đã chọn kèm
bảng thực nghiệm nhiều ngưỡng]]

### 4.2.1 So sánh Apriori và FP-Growth
[[BẢNG THẬT: n_itemsets, runtime_sec của từng thuật toán, itemsets_equal]]

### 4.2.2 Một số luật kết hợp tiêu biểu
[[BẢNG THẬT: top_rules_preview từ metrics.json]]

## 4.3 Kết quả tích hợp vào hệ thống webapp
[[ẢNH CHỤP MÀN HÌNH THẬT: trang chi tiết sản phẩm có khối khuyến nghị,
trang giỏ hàng có khối gợi ý tổng hợp, trang quản trị luật kết hợp]]

## 4.4 Kiểm thử
| Mã test | Tình huống | Kết quả |
|---|---|---|
| TC01 | Chạy `run_pipeline.py` từ đầu | [[Pass/Fail thật]] |
| TC02 | So sánh itemsets Apriori vs FP-Growth | [[Pass/Fail thật]] |
| TC03 | `dotnet build` + `dotnet test` | [[Pass/Fail thật, số test]] |
| TC04 | Mở trang chi tiết sản phẩm có luật → hiển thị đúng khuyến nghị | [[Pass/Fail thật]] |
| TC05 | Thêm nhiều sản phẩm vào giỏ → gợi ý tổng hợp đúng quy tắc gộp | [[Pass/Fail thật]] |
| TC06 | Reseed dữ liệu khi đã có đơn hàng → không lỗi, không mất đơn hàng | [[Pass/Fail thật]] |

---

# CHƯƠNG 5. KẾT LUẬN

## 5.1 Đánh giá so với mục tiêu
[[Viết sau khi có kết quả thật — đối chiếu với mục tiêu ở 1.4]]

## 5.2 Hạn chế
- Dữ liệu bị giới hạn ở 300 sản phẩm bán chạy nhất (TOP_N_ITEMS) để đảm
  bảo hiệu năng khai phá, có thể bỏ sót luật liên quan tới sản phẩm ít
  phổ biến hơn.
- Luật kết hợp xuất cho webapp chỉ ở dạng 1→1 để đơn giản hoá tra cứu,
  chưa tận dụng hết các luật nhiều-tới-một tìm được trong quá trình khai
  phá.
- Giỏ hàng lưu theo Session, chưa có tài khoản người dùng thật/lịch sử
  mua hàng cá nhân hoá.
- Mô hình luật kết hợp không tự động cập nhật theo thời gian thực (batch,
  cần chạy lại pipeline thủ công khi có dữ liệu giao dịch mới).

## 5.3 Hướng phát triển
- Bổ sung tài khoản người dùng thật, cá nhân hoá khuyến nghị theo lịch sử
  mua hàng từng khách hàng.
- Lập lịch tự động chạy lại pipeline khai phá theo chu kỳ, tự động cập
  nhật `rules.csv` mới nhất vào hệ thống.
- Kết hợp thêm kỹ thuật collaborative filtering để bổ sung cho luật kết
  hợp trong các trường hợp dữ liệu thưa.

---

# TÀI LIỆU THAM KHẢO
[1] R. Agrawal, R. Srikant (1994). *Fast Algorithms for Mining Association
Rules*. Proceedings of the 20th VLDB Conference.
[2] J. Han, J. Pei, Y. Yin (2000). *Mining Frequent Patterns without
Candidate Generation*. ACM SIGMOD.
[3] Chen, D. (2019). *Online Retail II* [Dataset]. UCI Machine Learning
Repository. https://doi.org/10.24432/C5CG6D
[4] Lê Hữu Dũng. *Lecture Note — Nhập môn Khai phá dữ liệu và Máy học*,
Trường Đại học Mở Hà Nội, 2024.
[5] Microsoft. *ASP.NET Core documentation*. https://learn.microsoft.com/aspnet/core/
[6] mlxtend documentation. https://rasbt.github.io/mlxtend/
