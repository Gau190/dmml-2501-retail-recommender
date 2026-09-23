namespace RetailRecommender.Web.Models;

public record Recommendation(Product Product, double Confidence, double Lift);
