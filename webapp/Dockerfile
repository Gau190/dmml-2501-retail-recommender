# Build context: webapp/ (see render.yaml dockerContext)
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

COPY src/RetailRecommender.Web/RetailRecommender.Web.csproj src/RetailRecommender.Web/
RUN dotnet restore src/RetailRecommender.Web/RetailRecommender.Web.csproj

COPY src/RetailRecommender.Web/ src/RetailRecommender.Web/
RUN dotnet publish src/RetailRecommender.Web/RetailRecommender.Web.csproj -c Release -o /app/publish --no-restore

FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /app/publish .

ENV ASPNETCORE_ENVIRONMENT=Production
EXPOSE 8080
ENTRYPOINT ["dotnet", "RetailRecommender.Web.dll"]
