# RetailRecommender

ASP.NET Core MVC (.NET 8) tích hợp gợi ý sản phẩm từ luật kết hợp. Dữ liệu mẫu nằm trong `src/RetailRecommender.Web/SeedData/` và được nạp mỗi lần khởi động: Product được upsert theo SKU, còn AssociationRule được xóa rồi nạp lại.

Ứng dụng dùng SQLite cùng `EnsureCreated()`; đây là lựa chọn phù hợp phạm vi bài tập, không dùng migrations.

Chạy bằng `dotnet run --project src/RetailRecommender.Web` từ thư mục `webapp/`.
