using Microsoft.AspNetCore.Mvc;
using RetailRecommender.Web.Data;
using RetailRecommender.Web.Services;
using Microsoft.EntityFrameworkCore;

namespace RetailRecommender.Web.Controllers;
public class ProductsController(AppDbContext db, IRecommendationService recommendations) : Controller
{
    private const int PageSize = 24;

    public IActionResult Index(string? q, int page = 1)
    {
        var query = db.Products.AsQueryable();
        var searchTerm = q?.Trim();
        if (!string.IsNullOrWhiteSpace(searchTerm))
        {
            var pattern = $"%{searchTerm}%";
            query = query.Where(p => EF.Functions.Like(p.Description, pattern) || EF.Functions.Like(p.Sku, pattern));
        }

        var totalCount = query.Count();
        var totalPages = Math.Max(1, (int)Math.Ceiling(totalCount / (double)PageSize));
        page = Math.Clamp(page, 1, totalPages);

        var model = new ProductListViewModel
        {
            Products = query.OrderBy(p => p.Description).Skip((page - 1) * PageSize).Take(PageSize).ToList(),
            Query = searchTerm ?? string.Empty,
            Page = page,
            TotalPages = totalPages,
            TotalCount = totalCount,
            RecommendedSkus = db.AssociationRules.Select(r => r.AntecedentSku).Distinct().ToHashSet()
        };

        return View(model);
    }
    public IActionResult Details(string sku)
    {
        var product = db.Products.SingleOrDefault(p => p.Sku == sku.Trim().ToUpperInvariant());
        if (product is null) return NotFound();
        ViewBag.Recommendations = recommendations.GetRecommendationsForProduct(product.Sku);
        return View(product);
    }
}

public class ProductListViewModel
{
    public IReadOnlyList<RetailRecommender.Web.Models.Product> Products { get; init; } = [];
    public string Query { get; init; } = string.Empty;
    public int Page { get; init; }
    public int TotalPages { get; init; }
    public int TotalCount { get; init; }
    public HashSet<string> RecommendedSkus { get; init; } = [];
}
