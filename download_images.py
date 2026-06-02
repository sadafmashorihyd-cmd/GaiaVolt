import os
import time
from icrawler.builtin import GoogleImageCrawler

# Cycling already done — baaki classes
classes_needed = {
    'led_lighting': 130,
    'ocean_cleanup': 130,
    'organic_farming': 130,
    'public_transport': 130,
    'water_conservation': 130,
    'wind_energy': 130
}

search_queries = {
    'led_lighting': 'LED light bulb energy saving indoor',
    'ocean_cleanup': 'ocean cleanup plastic waste sea',
    'organic_farming': 'organic farming vegetables crops field',
    'public_transport': 'public bus metro train station',
    'water_conservation': 'water conservation saving tap rain',
    'wind_energy': 'wind turbine farm energy field'
}

for cls, count in classes_needed.items():
    print(f"\n📥 Downloading {count} images for: {cls}")
    
    save_path = f'dataset/train/{cls}'
    os.makedirs(save_path, exist_ok=True)
    
    crawler = GoogleImageCrawler(
        storage={'root_dir': save_path}
    )
    crawler.crawl(
        keyword=search_queries[cls],
        max_num=count,
        min_size=(200, 200)
    )
    print(f"✅ {cls} done!")
    time.sleep(3)

print("\n🎉 All downloads complete!")