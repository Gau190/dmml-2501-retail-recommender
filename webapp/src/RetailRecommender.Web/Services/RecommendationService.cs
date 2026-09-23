using RetailRecommender.Web.Data;
using RetailRecommender.Web.Models;

namespace RetailRecommender.Web.Services;

public class RecommendationService(AppDbContext db) : IRecommendationService
{
    public IReadOnlyList<Recommendation> GetRecommendationsForProduct(string sku, int topN = 4)
    {
        sku = sku.Trim().ToUpperInvariant();
        return (from rule in db.AssociationRules
                join product in db.Products on rule.ConsequentSku equals product.Sku
                where rule.AntecedentSku == sku && rule.ConsequentSku != sku
                orderby rule.Confidence descending, rule.Lift descending
                select new Recommendation(product, rule.Confidence, rule.Lift)).Take(topN).ToList();
    }

    public IReadOnlyList<Recommendation> GetRecommendationsForCart(IEnumerable<string> cartSkus, int topN = 6)
    {
        var cart = cartSkus.Select(s => s.Trim().ToUpperInvariant()).ToHashSet();
        if (cart.Count == 0) return [];
        var candidates = db.AssociationRules.Where(r => cart.Contains(r.AntecedentSku) && !cart.Contains(r.ConsequentSku)).ToList()
            .GroupBy(r => r.ConsequentSku)
            .Select(g => g.OrderByDescending(r => r.Confidence).ThenByDescending(r => r.Lift).First())
            .OrderByDescending(r => r.Confidence).ThenByDescending(r => r.Lift).ThenBy(r => r.ConsequentSku)
            .Take(topN).ToList();
        var products = db.Products.Where(p => candidates.Select(r => r.ConsequentSku).Contains(p.Sku)).ToDictionary(p => p.Sku);
        return candidates.Where(r => products.ContainsKey(r.ConsequentSku)).Select(r => new Recommendation(products[r.ConsequentSku], r.Confidence, r.Lift)).ToList();
    }
}
