namespace RetailRecommender.Web.Models;

/// <summary>Attribution for one openly-licensed illustrative image (Openverse), required by its
/// Creative Commons license. Images are matched by product-type keyword, not the literal product.</summary>
public class ImageCredit
{
    public int Id { get; set; }
    public string ImageUrl { get; set; } = string.Empty;
    public string Title { get; set; } = string.Empty;
    public string Creator { get; set; } = string.Empty;
    public string CreatorUrl { get; set; } = string.Empty;
    public string License { get; set; } = string.Empty;
    public string LicenseUrl { get; set; } = string.Empty;
    public string SourceUrl { get; set; } = string.Empty;
}
