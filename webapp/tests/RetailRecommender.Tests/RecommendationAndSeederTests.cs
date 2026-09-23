using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging.Abstractions;
using RetailRecommender.Web.Data;
using RetailRecommender.Web.Models;
using RetailRecommender.Web.Services;

namespace RetailRecommender.Tests;

public class RecommendationAndSeederTests
{
    private static AppDbContext Context()
    {
        var options = new DbContextOptionsBuilder<AppDbContext>().UseInMemoryDatabase(Guid.NewGuid().ToString()).Options;
        return new AppDbContext(options);
    }
    private static void Products(AppDbContext db, params string[] skus)
    {
        db.Products.AddRange(skus.Select(s => new Product { Sku = s, Description = s, UnitPrice = 1, Category = "General" })); db.SaveChanges();
    }

    [Fact]
    public void Product_recommendations_sort_by_confidence_then_lift()
    {
        using var db = Context(); Products(db, "A", "B", "C", "D");
        db.AssociationRules.AddRange(new AssociationRule { AntecedentSku = "A", ConsequentSku = "B", Confidence = .5, Lift = 9 }, new AssociationRule { AntecedentSku = "A", ConsequentSku = "C", Confidence = .8, Lift = 1 }, new AssociationRule { AntecedentSku = "A", ConsequentSku = "D", Confidence = .8, Lift = 2 }); db.SaveChanges();
        var result = new RecommendationService(db).GetRecommendationsForProduct("a");
        Assert.Equal(["D", "C", "B"], result.Select(x => x.Product.Sku));
    }

    [Fact]
    public void Product_recommendations_exclude_self_rule()
    {
        using var db = Context(); Products(db, "A", "B"); db.AssociationRules.AddRange(new AssociationRule { AntecedentSku = "A", ConsequentSku = "A", Confidence = 1, Lift = 10 }, new AssociationRule { AntecedentSku = "A", ConsequentSku = "B", Confidence = .4, Lift = 1 }); db.SaveChanges();
        Assert.Equal(["B"], new RecommendationService(db).GetRecommendationsForProduct("A").Select(x => x.Product.Sku));
    }

    [Fact]
    public void Cart_recommendations_exclude_cart_and_aggregate_by_max_confidence()
    {
        using var db = Context(); Products(db, "A", "B", "C", "D");
        db.AssociationRules.AddRange(
            new AssociationRule { AntecedentSku = "A", ConsequentSku = "B", Confidence = .99, Lift = 9 },
            new AssociationRule { AntecedentSku = "A", ConsequentSku = "C", Confidence = .7, Lift = 1 },
            new AssociationRule { AntecedentSku = "B", ConsequentSku = "C", Confidence = .8, Lift = 2 },
            new AssociationRule { AntecedentSku = "A", ConsequentSku = "D", Confidence = .8, Lift = 1 }); db.SaveChanges();
        var result = new RecommendationService(db).GetRecommendationsForCart(["A", "B"]);
        Assert.Equal(["C", "D"], result.Select(x => x.Product.Sku));
        Assert.Equal(.8, result.First().Confidence);
        Assert.Equal(2, result.First().Lift);
    }

    [Fact]
    public void Product_without_rules_returns_empty()
    {
        using var db = Context(); Products(db, "A");
        Assert.Empty(new RecommendationService(db).GetRecommendationsForProduct("A"));
    }

    [Fact]
    public void Csv_importer_handles_rfc4180_invariant_numbers_and_invalid_rules()
    {
        using var db = Context(); var dir = WriteSeed("sku,description,unit_price,category\nA,\"CERAMIC, HEART \"\"SHAPE\"\" MUG\",3.75,General\nB,Other,2.00,General\n", "antecedent_sku,consequent_sku,support,confidence,lift\nA,B,0.1,0.75,1.5\nA,B,0.1,0.75,1.5\nA,Z,0.1,0.5,1.2\n");
        try { new DataSeeder(db, NullLogger<DataSeeder>.Instance).Seed(dir); }
        finally { Directory.Delete(dir, true); }
        var product = Assert.Single(db.Products.Where(p => p.Sku == "A"));
        Assert.Equal("CERAMIC, HEART \"SHAPE\" MUG", product.Description); Assert.Equal(3.75m, product.UnitPrice); Assert.Single(db.AssociationRules);
    }

    [Fact]
    public void Reseed_preserves_referenced_products_and_replaces_rules()
    {
        using var db = Context();
        var first = WriteSeed("sku,description,unit_price,category\nA,Old,1.00,General\nB,Keep,2.00,General\n", "antecedent_sku,consequent_sku,support,confidence,lift\nA,B,0.1,0.5,1.2\n");
        var second = WriteSeed("sku,description,unit_price,category\nA,Updated,3.00,New\nC,New,4.00,General\n", "antecedent_sku,consequent_sku,support,confidence,lift\nA,C,0.2,0.9,2.1\n");
        try
        {
            var seeder = new DataSeeder(db, NullLogger<DataSeeder>.Instance); seeder.Seed(first);
            var b = db.Products.Single(p => p.Sku == "B"); var order = new Order { Items = [new OrderItem { ProductId = b.Id, Quantity = 1, UnitPrice = b.UnitPrice }] }; db.Orders.Add(order); db.SaveChanges();
            seeder.Seed(second);
            Assert.Equal("Updated", db.Products.Single(p => p.Sku == "A").Description);
            Assert.NotNull(db.Products.SingleOrDefault(p => p.Sku == "B")); Assert.Single(db.Orders); Assert.Single(db.OrderItems);
            var rule = Assert.Single(db.AssociationRules); Assert.Equal(("A", "C"), (rule.AntecedentSku, rule.ConsequentSku));
        }
        finally { Directory.Delete(first, true); Directory.Delete(second, true); }
    }

    [Fact]
    public void Csv_importer_reads_image_url_when_present_and_defaults_to_null()
    {
        using var db = Context();
        var dir = WriteSeed(
            "sku,description,unit_price,category,image_url\nA,Has image,1.00,General,https://example.org/a.jpg\nB,No image,2.00,General,\n",
            "antecedent_sku,consequent_sku,support,confidence,lift\n");
        try { new DataSeeder(db, NullLogger<DataSeeder>.Instance).Seed(dir); }
        finally { Directory.Delete(dir, true); }
        Assert.Equal("https://example.org/a.jpg", db.Products.Single(p => p.Sku == "A").ImageUrl);
        Assert.Null(db.Products.Single(p => p.Sku == "B").ImageUrl);
    }

    private static string WriteSeed(string products, string rules)
    {
        var dir = Path.Combine(Path.GetTempPath(), "retail-seed-" + Guid.NewGuid()); Directory.CreateDirectory(dir);
        File.WriteAllText(Path.Combine(dir, "products.csv"), products); File.WriteAllText(Path.Combine(dir, "rules.csv"), rules);
        return dir;
    }
}
