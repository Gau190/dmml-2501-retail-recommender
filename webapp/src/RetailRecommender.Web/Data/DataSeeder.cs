using System.Globalization;
using CsvHelper;
using CsvHelper.Configuration;
using CsvHelper.Configuration.Attributes;
using Microsoft.EntityFrameworkCore;
using RetailRecommender.Web.Models;

namespace RetailRecommender.Web.Data;

public class DataSeeder(AppDbContext db, ILogger<DataSeeder> logger)
{
    private readonly CsvConfiguration _csv = new(CultureInfo.InvariantCulture) { PrepareHeaderForMatch = args => args.Header.Trim().ToLowerInvariant() };

    public void Seed(string? seedDirectory = null)
    {
        seedDirectory ??= Path.Combine(AppContext.BaseDirectory, "SeedData");
        var productsPath = Path.Combine(seedDirectory, "products.csv");
        var rulesPath = Path.Combine(seedDirectory, "rules.csv");
        var products = ReadProducts(productsPath);
        foreach (var item in products)
        {
            var current = db.Products.SingleOrDefault(p => p.Sku == item.Sku);
            if (current is null) db.Products.Add(item);
            else { current.Description = item.Description; current.UnitPrice = item.UnitPrice; current.Category = item.Category; }
        }
        db.SaveChanges();

        db.AssociationRules.RemoveRange(db.AssociationRules);
        db.SaveChanges();
        var knownSkus = db.Products.Select(p => p.Sku).ToHashSet(StringComparer.OrdinalIgnoreCase);
        var seen = new HashSet<(string, string)>();
        foreach (var rule in ReadRules(rulesPath))
        {
            var key = (rule.AntecedentSku, rule.ConsequentSku);
            if (!knownSkus.Contains(rule.AntecedentSku) || !knownSkus.Contains(rule.ConsequentSku) || !seen.Add(key))
            {
                logger.LogWarning("Bỏ qua luật CSV không hợp lệ hoặc trùng: {Antecedent}->{Consequent}", rule.AntecedentSku, rule.ConsequentSku);
                continue;
            }
            db.AssociationRules.Add(rule);
        }
        db.SaveChanges();
    }

    private List<Product> ReadProducts(string path)
    {
        if (!File.Exists(path)) { logger.LogWarning("Không tìm thấy products.csv: {Path}", path); return []; }
        using var reader = new StreamReader(path);
        using var csv = new CsvReader(reader, _csv);
        return csv.GetRecords<ProductCsv>().Where(x => !string.IsNullOrWhiteSpace(x.Sku)).Select(x => new Product { Sku = x.Sku.Trim().ToUpperInvariant(), Description = x.Description, UnitPrice = x.UnitPrice, Category = string.IsNullOrWhiteSpace(x.Category) ? "General" : x.Category }).ToList();
    }

    private List<AssociationRule> ReadRules(string path)
    {
        if (!File.Exists(path)) { logger.LogWarning("Không tìm thấy rules.csv: {Path}; ứng dụng vẫn tiếp tục", path); return []; }
        using var reader = new StreamReader(path);
        using var csv = new CsvReader(reader, _csv);
        return csv.GetRecords<RuleCsv>().Select(x => new AssociationRule { AntecedentSku = x.AntecedentSku.Trim().ToUpperInvariant(), ConsequentSku = x.ConsequentSku.Trim().ToUpperInvariant(), Support = x.Support, Confidence = x.Confidence, Lift = x.Lift }).ToList();
    }

    private sealed class ProductCsv { [Name("sku")] public string Sku { get; set; } = ""; [Name("description")] public string Description { get; set; } = ""; [Name("unit_price")] public decimal UnitPrice { get; set; } [Name("category")] public string Category { get; set; } = "General"; }
    private sealed class RuleCsv { [Name("antecedent_sku")] public string AntecedentSku { get; set; } = ""; [Name("consequent_sku")] public string ConsequentSku { get; set; } = ""; [Name("support")] public double Support { get; set; } [Name("confidence")] public double Confidence { get; set; } [Name("lift")] public double Lift { get; set; } }
}
