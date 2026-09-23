using Microsoft.AspNetCore.Mvc;
using RetailRecommender.Web.Data;

namespace RetailRecommender.Web.Controllers;

public class ImageCreditsController(AppDbContext db) : Controller
{
    public IActionResult Index() => View(db.ImageCredits.OrderBy(c => c.Title).ToList());
}
