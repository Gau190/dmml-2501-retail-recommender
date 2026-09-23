using Microsoft.EntityFrameworkCore;
using RetailRecommender.Web.Models;

namespace RetailRecommender.Web.Data;

public class AppDbContext(DbContextOptions<AppDbContext> options) : DbContext(options)
{
    public DbSet<Product> Products => Set<Product>();
    public DbSet<AssociationRule> AssociationRules => Set<AssociationRule>();
    public DbSet<Order> Orders => Set<Order>();
    public DbSet<OrderItem> OrderItems => Set<OrderItem>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Product>().HasIndex(p => p.Sku).IsUnique();
        modelBuilder.Entity<AssociationRule>().HasIndex(r => new { r.AntecedentSku, r.ConsequentSku }).IsUnique();
        modelBuilder.Entity<OrderItem>().HasOne(i => i.Product).WithMany().HasForeignKey(i => i.ProductId).OnDelete(DeleteBehavior.Restrict);
        modelBuilder.Entity<OrderItem>().HasOne(i => i.Order).WithMany(o => o.Items).HasForeignKey(i => i.OrderId);
    }
}
