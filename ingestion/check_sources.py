import sys
sys.path.insert(0, '.')
import config

sources_by_country = {}
for name, source in config.SOURCES.items():
    country = source.get('country', 'OTHER')
    sources_by_country[country] = sources_by_country.get(country, 0) + 1

print("Sources by country:")
for country in sorted(sources_by_country.keys()):
    print(f"  {country}: {sources_by_country[country]} sources")
print(f"\nTotal sources: {sum(sources_by_country.values())}")
