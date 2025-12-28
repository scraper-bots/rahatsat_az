"""
Business Analytics Chart Generator for Rahatsat.az Car Marketplace
Generates business-focused visualizations for executive decision-making
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Set professional style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Load and prepare data
print("Loading dataset...")
df = pd.read_csv('rahatsat_cars.csv')

# Clean price column
def clean_price(price_str):
    """Convert price strings to numeric values"""
    if pd.isna(price_str) or price_str == 'Razılaşma yolu ilə':
        return np.nan
    price_str = str(price_str).replace('min:', '').replace('AZN', '').replace(',', '').replace(' ', '')
    try:
        return float(price_str)
    except:
        return np.nan

df['price_numeric'] = df['price'].apply(clean_price)

# Clean engine volume
def clean_engine(engine_str):
    """Convert engine volume to numeric"""
    if pd.isna(engine_str):
        return np.nan
    engine_str = str(engine_str).replace(',', '.').replace(' ', '')
    try:
        return float(engine_str)
    except:
        return np.nan

df['engine_numeric'] = df['engine_volume'].apply(clean_engine)

# Simplify location to city level
def simplify_location(location):
    """Extract main city from location"""
    if pd.isna(location):
        return 'Unknown'
    if 'Bakı' in location or 'Baki' in location:
        return 'Bakı'
    return location.split(',')[0].strip()

df['city'] = df['location'].apply(simplify_location)

print(f"Loaded {len(df)} listings")
print("Generating business analytics charts...\n")

# Chart 1: Market Share by Brand
print("1. Generating Market Share by Brand...")
fig, ax = plt.subplots(figsize=(12, 6))
brand_counts = df['brand'].value_counts().head(10)
colors = plt.cm.Set3(range(len(brand_counts)))
bars = ax.bar(range(len(brand_counts)), brand_counts.values, color=colors, edgecolor='black', linewidth=1.2)
ax.set_xticks(range(len(brand_counts)))
ax.set_xticklabels(brand_counts.index, rotation=45, ha='right', fontsize=10, fontweight='bold')
ax.set_ylabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Market Share: Top 10 Brands by Listing Volume', fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)

# Add value labels on bars
for i, (bar, value) in enumerate(zip(bars, brand_counts.values)):
    percentage = (value / len(df)) * 100
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f'{value}\n({percentage:.1f}%)',
            ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/01_market_share_by_brand.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✓ Saved: charts/01_market_share_by_brand.png")

# Chart 2: Average Price by Brand
print("2. Generating Average Price by Brand...")
fig, ax = plt.subplots(figsize=(12, 7))
brand_price = df.groupby('brand')['price_numeric'].agg(['mean', 'count'])
brand_price = brand_price[brand_price['count'] >= 2].sort_values('mean', ascending=True)
colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(brand_price)))
bars = ax.barh(range(len(brand_price)), brand_price['mean'], color=colors, edgecolor='black', linewidth=1.2)
ax.set_yticks(range(len(brand_price)))
ax.set_yticklabels(brand_price.index, fontsize=10, fontweight='bold')
ax.set_xlabel('Average Price (AZN)', fontsize=12, fontweight='bold')
ax.set_title('Premium vs Budget Brands: Average Listing Price', fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='x', alpha=0.3)

# Add value labels
for i, (bar, value) in enumerate(zip(bars, brand_price['mean'])):
    ax.text(value + 500, bar.get_y() + bar.get_height()/2,
            f'{value:,.0f} AZN',
            ha='left', va='center', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/02_average_price_by_brand.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✓ Saved: charts/02_average_price_by_brand.png")

# Chart 3: Geographic Distribution
print("3. Generating Geographic Distribution...")
fig, ax = plt.subplots(figsize=(12, 6))
city_counts = df['city'].value_counts().head(10)
colors = plt.cm.Spectral(np.linspace(0, 1, len(city_counts)))
bars = ax.bar(range(len(city_counts)), city_counts.values, color=colors, edgecolor='black', linewidth=1.2)
ax.set_xticks(range(len(city_counts)))
ax.set_xticklabels(city_counts.index, rotation=45, ha='right', fontsize=10, fontweight='bold')
ax.set_ylabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Geographic Market Concentration: Top 10 Cities', fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)

# Add value labels and percentages
for bar, value in zip(bars, city_counts.values):
    percentage = (value / len(df)) * 100
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f'{value}\n({percentage:.1f}%)',
            ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/03_geographic_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✓ Saved: charts/03_geographic_distribution.png")

# Chart 4: Price Segmentation
print("4. Generating Price Segmentation Analysis...")
price_bins = [0, 5000, 10000, 15000, 20000, 30000, 50000]
price_labels = ['Budget\n(0-5K)', 'Economy\n(5-10K)', 'Mid-Range\n(10-15K)',
                'Premium\n(15-20K)', 'Luxury\n(20-30K)', 'Ultra-Luxury\n(30K+)']
df['price_segment'] = pd.cut(df['price_numeric'], bins=price_bins, labels=price_labels, include_lowest=True)

fig, ax = plt.subplots(figsize=(12, 6))
segment_counts = df['price_segment'].value_counts().sort_index()
colors = ['#FF6B6B', '#FFA06B', '#FFD93D', '#6BCF7F', '#4ECDC4', '#45B7D1']
bars = ax.bar(range(len(segment_counts)), segment_counts.values, color=colors, edgecolor='black', linewidth=1.2)
ax.set_xticks(range(len(segment_counts)))
ax.set_xticklabels(segment_counts.index, fontsize=10, fontweight='bold')
ax.set_ylabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Market Segmentation by Price Range', fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)

# Add value labels
for bar, value in zip(bars, segment_counts.values):
    if pd.notna(value):
        percentage = (value / df['price_numeric'].notna().sum()) * 100
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f'{int(value)}\n({percentage:.1f}%)',
                ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/04_price_segmentation.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✓ Saved: charts/04_price_segmentation.png")

# Chart 5: Transmission Type Distribution
print("5. Generating Transmission Type Distribution...")
fig, ax = plt.subplots(figsize=(10, 6))
trans_counts = df['transmission'].value_counts()
colors = ['#3498db', '#e74c3c', '#2ecc71']
bars = ax.bar(range(len(trans_counts)), trans_counts.values, color=colors, edgecolor='black', linewidth=1.2)
ax.set_xticks(range(len(trans_counts)))
ax.set_xticklabels(trans_counts.index, fontsize=11, fontweight='bold')
ax.set_ylabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Customer Preference: Transmission Types', fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)

# Add value labels
for bar, value in zip(bars, trans_counts.values):
    percentage = (value / df['transmission'].notna().sum()) * 100
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{value}\n({percentage:.1f}%)',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/05_transmission_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✓ Saved: charts/05_transmission_distribution.png")

# Chart 6: Body Type Distribution
print("6. Generating Body Type Distribution...")
fig, ax = plt.subplots(figsize=(11, 6))
body_counts = df['body_type'].value_counts()
colors = plt.cm.Set2(range(len(body_counts)))
bars = ax.bar(range(len(body_counts)), body_counts.values, color=colors, edgecolor='black', linewidth=1.2)
ax.set_xticks(range(len(body_counts)))
ax.set_xticklabels(body_counts.index, fontsize=11, fontweight='bold', rotation=15, ha='right')
ax.set_ylabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Market Demand by Vehicle Type', fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)

# Add value labels
for bar, value in zip(bars, body_counts.values):
    percentage = (value / df['body_type'].notna().sum()) * 100
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{value}\n({percentage:.1f}%)',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/06_body_type_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✓ Saved: charts/06_body_type_distribution.png")

# Chart 7: Fuel Type Distribution
print("7. Generating Fuel Type Distribution...")
fig, ax = plt.subplots(figsize=(10, 6))
fuel_counts = df['fuel_type'].value_counts()
colors = ['#F39C12', '#8E44AD', '#27AE60']
bars = ax.bar(range(len(fuel_counts)), fuel_counts.values, color=colors, edgecolor='black', linewidth=1.2)
ax.set_xticks(range(len(fuel_counts)))
ax.set_xticklabels(fuel_counts.index, fontsize=11, fontweight='bold')
ax.set_ylabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Fuel Type Preferences in Market', fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)

# Add value labels
for bar, value in zip(bars, fuel_counts.values):
    percentage = (value / df['fuel_type'].notna().sum()) * 100
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.8,
            f'{value}\n({percentage:.1f}%)',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/07_fuel_type_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✓ Saved: charts/07_fuel_type_distribution.png")

# Chart 8: Vehicle Age Distribution
print("8. Generating Vehicle Age Distribution...")
fig, ax = plt.subplots(figsize=(14, 6))
year_counts = df['year'].value_counts().sort_index()
# Filter to reasonable years (after 2000 for better visualization)
year_counts_recent = year_counts[year_counts.index >= 2000]
colors = plt.cm.viridis(np.linspace(0, 1, len(year_counts_recent)))
ax.plot(year_counts_recent.index, year_counts_recent.values, marker='o', linewidth=2.5,
        markersize=8, color='#E74C3C', markerfacecolor='#3498DB', markeredgewidth=2, markeredgecolor='#E74C3C')
ax.fill_between(year_counts_recent.index, year_counts_recent.values, alpha=0.3, color='#3498DB')
ax.set_xlabel('Model Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Inventory Distribution by Vehicle Age (2000+)', fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3)

# Add value labels for peaks
max_idx = year_counts_recent.values.argmax()
max_year = year_counts_recent.index[max_idx]
max_value = year_counts_recent.values[max_idx]
ax.annotate(f'Peak: {max_year}\n{max_value} listings',
            xy=(max_year, max_value), xytext=(max_year-2, max_value+1),
            fontsize=10, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', color='black', lw=2))

plt.tight_layout()
plt.savefig('charts/08_vehicle_age_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✓ Saved: charts/08_vehicle_age_distribution.png")

# Chart 9: Price vs Year Relationship
print("9. Generating Price vs Year Relationship...")
fig, ax = plt.subplots(figsize=(12, 6))
year_price = df[df['year'] >= 2000].groupby('year')['price_numeric'].mean().dropna()
colors = plt.cm.plasma(np.linspace(0.2, 0.8, len(year_price)))
bars = ax.bar(year_price.index, year_price.values, color=colors, edgecolor='black', linewidth=1)
ax.set_xlabel('Model Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Average Price (AZN)', fontsize=12, fontweight='bold')
ax.set_title('Vehicle Depreciation: Average Price by Model Year', fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)

# Add trend line
z = np.polyfit(year_price.index, year_price.values, 1)
p = np.poly1d(z)
ax.plot(year_price.index, p(year_price.index), "r--", linewidth=2.5, label=f'Trend Line', alpha=0.8)
ax.legend(fontsize=10, loc='upper left')

plt.tight_layout()
plt.savefig('charts/09_price_vs_year.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✓ Saved: charts/09_price_vs_year.png")

# Chart 10: Mileage vs Price Relationship
print("10. Generating Mileage vs Price Analysis...")
fig, ax = plt.subplots(figsize=(12, 6))
# Create mileage bins
mileage_bins = [0, 50000, 100000, 150000, 200000, 300000, 500000]
mileage_labels = ['0-50K', '50-100K', '100-150K', '150-200K', '200-300K', '300K+']
df['mileage_segment'] = pd.cut(df['mileage'], bins=mileage_bins, labels=mileage_labels, include_lowest=True)
mileage_price = df.groupby('mileage_segment')['price_numeric'].mean().dropna()

colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(mileage_price)))
bars = ax.bar(range(len(mileage_price)), mileage_price.values, color=colors, edgecolor='black', linewidth=1.2)
ax.set_xticks(range(len(mileage_price)))
ax.set_xticklabels(mileage_price.index, fontsize=10, fontweight='bold')
ax.set_xlabel('Mileage Range (km)', fontsize=12, fontweight='bold')
ax.set_ylabel('Average Price (AZN)', fontsize=12, fontweight='bold')
ax.set_title('Impact of Mileage on Vehicle Value', fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)

# Add value labels
for bar, value in zip(bars, mileage_price.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 300,
            f'{value:,.0f}',
            ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/10_mileage_vs_price.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✓ Saved: charts/10_mileage_vs_price.png")

# Chart 11: Premium vs Budget Market Analysis
print("11. Generating Premium vs Budget Market Analysis...")
fig, ax = plt.subplots(figsize=(12, 7))

# Define segments
budget_threshold = 10000
premium_threshold = 20000

segments = []
for price in df['price_numeric']:
    if pd.isna(price):
        segments.append('Unknown')
    elif price < budget_threshold:
        segments.append('Budget (<10K AZN)')
    elif price < premium_threshold:
        segments.append('Mid-Market (10-20K AZN)')
    else:
        segments.append('Premium (>20K AZN)')

df['market_segment'] = segments
segment_counts = df['market_segment'].value_counts()

# Reorder for better presentation
order = ['Budget (<10K AZN)', 'Mid-Market (10-20K AZN)', 'Premium (>20K AZN)']
segment_counts = segment_counts.reindex([s for s in order if s in segment_counts.index])

colors = ['#FF6B6B', '#FFD93D', '#4ECDC4']
bars = ax.bar(range(len(segment_counts)), segment_counts.values, color=colors, edgecolor='black', linewidth=1.5)
ax.set_xticks(range(len(segment_counts)))
ax.set_xticklabels(segment_counts.index, fontsize=11, fontweight='bold')
ax.set_ylabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Market Composition: Budget vs Mid-Market vs Premium', fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)

# Add value labels
total_with_price = df['price_numeric'].notna().sum()
for bar, value in zip(bars, segment_counts.values):
    percentage = (value / total_with_price) * 100
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{value}\n({percentage:.1f}%)',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/11_market_segment_analysis.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✓ Saved: charts/11_market_segment_analysis.png")

# Chart 12: Top Brands by Price Segment
print("12. Generating Brand Performance by Market Segment...")
fig, ax = plt.subplots(figsize=(14, 7))

# Get top brands
top_brands = df['brand'].value_counts().head(8).index
df_top_brands = df[df['brand'].isin(top_brands)]

# Create cross-tabulation
segment_brand = pd.crosstab(df_top_brands['market_segment'], df_top_brands['brand'])
segment_brand = segment_brand.reindex(['Budget (<10K AZN)', 'Mid-Market (10-20K AZN)', 'Premium (>20K AZN)'])
segment_brand = segment_brand.fillna(0)

# Create stacked bar chart
segment_brand.plot(kind='bar', stacked=True, ax=ax, colormap='tab10',
                   edgecolor='black', linewidth=1.2, width=0.7)
ax.set_xlabel('Market Segment', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Brand Positioning Across Market Segments', fontsize=14, fontweight='bold', pad=20)
ax.set_xticklabels(ax.get_xticklabels(), rotation=15, ha='right', fontsize=10, fontweight='bold')
ax.legend(title='Brand', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('charts/12_brand_positioning_by_segment.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✓ Saved: charts/12_brand_positioning_by_segment.png")

# Chart 13: Transmission Preference by Price Segment
print("13. Generating Transmission Preference by Price Segment...")
fig, ax = plt.subplots(figsize=(12, 6))

trans_segment = pd.crosstab(df['market_segment'], df['transmission'])
trans_segment = trans_segment.reindex(['Budget (<10K AZN)', 'Mid-Market (10-20K AZN)', 'Premium (>20K AZN)'])

trans_segment.plot(kind='bar', ax=ax, color=['#3498db', '#e74c3c', '#2ecc71'],
                   edgecolor='black', linewidth=1.2, width=0.65)
ax.set_xlabel('Market Segment', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Transmission Type Preferences Across Market Segments', fontsize=14, fontweight='bold', pad=20)
ax.set_xticklabels(ax.get_xticklabels(), rotation=15, ha='right', fontsize=10, fontweight='bold')
ax.legend(title='Transmission', fontsize=10, title_fontsize=11)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('charts/13_transmission_by_segment.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✓ Saved: charts/13_transmission_by_segment.png")

print("\n" + "="*80)
print("✓ All charts generated successfully!")
print(f"✓ Total: 13 business analytics visualizations")
print(f"✓ Location: charts/ directory")
print("="*80)
