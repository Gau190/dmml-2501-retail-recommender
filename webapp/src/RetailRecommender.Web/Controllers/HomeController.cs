using Microsoft.AspNetCore.Mvc;
using RetailRecommender.Web.Data;

namespace RetailRecommender.Web.Controllers;
public class HomeController(AppDbContext db) : Controller
{
    public IActionResult Index() => View(db.Products.OrderBy(p => p.Category).ThenBy(p => p.Description).ToList());
}
