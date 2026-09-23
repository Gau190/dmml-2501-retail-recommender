using Microsoft.AspNetCore.Mvc;
using RetailRecommender.Web.Data;
namespace RetailRecommender.Web.Controllers;
public class AdminController(AppDbContext db) : Controller
{
    public IActionResult Rules() => View(db.AssociationRules.OrderByDescending(r => r.Confidence).ThenByDescending(r => r.Lift).ToList());
}
