using Microsoft.AspNetCore.Mvc;
using RetailRecommender.Web.Data;

namespace RetailRecommender.Web.Controllers;
public class HomeController(AppDbContext db) : Controller
{
    public IActionResult Index()
    {
        var ruleCounts = db.AssociationRules
            .GroupBy(r => r.AntecedentSku)
            .Select(g => new { Sku = g.Key, Count = g.Count() });

        var featuredProducts = db.Products
            .Join(ruleCounts, p => p.Sku, r => r.Sku, (p, r) => new { Product = p, r.Count })
            .OrderByDescending(x => x.Count)
            .ThenBy(x => x.Product.Description)
            .Take(12)
            .Select(x => x.Product)
            .ToList();

        ViewBag.ProductCount = db.Products.Count();
        ViewBag.RuleCount = db.AssociationRules.Count();
        ViewBag.RecommendedProductCount = ruleCounts.Count();
        return View(featuredProducts);
    }
}
