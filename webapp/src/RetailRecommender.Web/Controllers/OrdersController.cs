using System.Text.Json;
using Microsoft.AspNetCore.Mvc;
using RetailRecommender.Web.Data;
using RetailRecommender.Web.Models;

namespace RetailRecommender.Web.Controllers;
public class OrdersController(AppDbContext db) : Controller
{
    [HttpPost] public IActionResult Checkout()
    {
        var cart = JsonSerializer.Deserialize<Dictionary<string, int>>(HttpContext.Session.GetString("cart") ?? "{}") ?? [];
        var products = db.Products.Where(p => cart.Keys.Contains(p.Sku)).ToList();
        if (products.Count == 0) return RedirectToAction("Index", "Cart");
        var order = new Order { Items = products.Select(p => new OrderItem { ProductId = p.Id, Quantity = cart[p.Sku], UnitPrice = p.UnitPrice }).ToList() };
        db.Orders.Add(order); db.SaveChanges(); HttpContext.Session.Remove("cart");
        TempData["Message"] = $"Đặt hàng #{order.Id} thành công."; return RedirectToAction("Index", "Home");
    }
}
