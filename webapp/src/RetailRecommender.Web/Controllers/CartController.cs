using System.Text.Json;
using Microsoft.AspNetCore.Mvc;
using RetailRecommender.Web.Data;
using RetailRecommender.Web.Models;
using RetailRecommender.Web.Services;

namespace RetailRecommender.Web.Controllers;
public class CartController(AppDbContext db, IRecommendationService recommendations) : Controller
{
    public IActionResult Index()
    {
        var cart = GetCart(); var skus = cart.Keys.ToList();
        var products = db.Products.Where(p => skus.Contains(p.Sku)).ToDictionary(p => p.Sku);
        ViewBag.Recommendations = recommendations.GetRecommendationsForCart(skus);
        return View(cart.Where(x => products.ContainsKey(x.Key)).Select(x => new CartLine(products[x.Key], x.Value)).ToList());
    }
    [HttpPost] public IActionResult Add(string sku)
    {
        var cart = GetCart(); sku = sku.Trim().ToUpperInvariant(); cart[sku] = cart.GetValueOrDefault(sku) + 1; SaveCart(cart);
        return RedirectToAction("Index");
    }
    [HttpPost] public IActionResult Remove(string sku)
    {
        var cart = GetCart(); cart.Remove(sku.Trim().ToUpperInvariant()); SaveCart(cart); return RedirectToAction("Index");
    }
    private Dictionary<string, int> GetCart() => JsonSerializer.Deserialize<Dictionary<string, int>>(HttpContext.Session.GetString("cart") ?? "{}") ?? [];
    private void SaveCart(Dictionary<string, int> cart) => HttpContext.Session.SetString("cart", JsonSerializer.Serialize(cart));
}
public record CartLine(Product Product, int Quantity);
