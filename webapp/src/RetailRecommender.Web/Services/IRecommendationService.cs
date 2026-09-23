using RetailRecommender.Web.Models;
namespace RetailRecommender.Web.Services;
public interface IRecommendationService
{
    IReadOnlyList<Recommendation> GetRecommendationsForProduct(string sku, int topN = 4);
    IReadOnlyList<Recommendation> GetRecommendationsForCart(IEnumerable<string> cartSkus, int topN = 6);
}
