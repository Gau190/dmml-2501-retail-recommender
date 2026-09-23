using Microsoft.AspNetCore.Mvc;
using RetailRecommender.Web.Data;
using RetailRecommender.Web.Services;

namespace RetailRecommender.Web.Controllers;
public class ProductsController(AppDbContext db, IRecommendationService recommendations) : Controller
{
    public IActionResult Index() => View(db.Products.OrderBy(p => p.Description).ToList());
    public IActionResult Details(string sku)
    {
        var product = db.Products.SingleOrDefault(p => p.Sku == sku.Trim().ToUpperInvariant());
        if (product is null) return NotFound();
        ViewBag.Recommendations = recommendations.GetRecommendationsForProduct(product.Sku);
        return View(product);
    }
}
