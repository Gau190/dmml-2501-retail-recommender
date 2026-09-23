using System.Text.Json;
using Microsoft.AspNetCore.Mvc;

namespace RetailRecommender.Web.ViewComponents;

public class CartSummaryViewComponent : ViewComponent
{
    public IViewComponentResult Invoke()
    {
        var cart = JsonSerializer.Deserialize<Dictionary<string, int>>(
            HttpContext.Session.GetString("cart") ?? "{}") ?? [];

        return View(cart.Values.Sum());
    }
}
