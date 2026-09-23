using System.ComponentModel.DataAnnotations;

namespace RetailRecommender.Web.Models;

public class Product
{
    public int Id { get; set; }
    [Required, MaxLength(64)] public string Sku { get; set; } = string.Empty;
    [Required] public string Description { get; set; } = string.Empty;
    public decimal UnitPrice { get; set; }
    [Required, MaxLength(128)] public string Category { get; set; } = "General";
}
