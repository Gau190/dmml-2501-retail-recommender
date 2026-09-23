namespace RetailRecommender.Web.Models;

public class AssociationRule
{
    public int Id { get; set; }
    public string AntecedentSku { get; set; } = string.Empty;
    public string ConsequentSku { get; set; } = string.Empty;
    public double Support { get; set; }
    public double Confidence { get; set; }
    public double Lift { get; set; }
}
