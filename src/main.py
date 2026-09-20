import json

with open("data/schemes.json", "r", encoding="utf-8") as file:
    schemes = json.load(file)


def search_schemes(keyword):
    keyword = keyword.lower()

    results = []

    for scheme in schemes:
        text = json.dumps(scheme).lower()

        if keyword in text:
            results.append(scheme)

    return results


query = input("What kind of government help do you need? ")

results = search_schemes(query)

print(f"\nFound {len(results)} scheme(s):")

for scheme in results:
    print(f"- {scheme['name']}")