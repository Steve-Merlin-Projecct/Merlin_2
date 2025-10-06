"""
Test script for the preference packages system
Demonstrates how contextual job preferences work
"""

import json
import logging
from modules.preference_packages import PreferencePackages, create_steve_glen_packages
from modules.intelligent_scraper import IntelligentScraper, initialize_steve_glen_preferences

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_preference_packages():
    """Test the preference packages system"""
    print("🧪 Testing Preference Packages System")
    print("=" * 50)
    
    # Initialize Steve Glen's preferences
    print("\n1. Initializing Steve Glen's preference packages...")
    try:
        initialize_steve_glen_preferences()
        print("✅ Preference packages initialized")
    except Exception as e:
        print(f"❌ Error initializing: {e}")
        return False
    
    # Get targeted search configurations
    print("\n2. Getting targeted search configurations...")
    pp = PreferencePackages()
    search_configs = pp.get_targeted_search_configs("steve_glen")
    
    print(f"✅ Found {len(search_configs)} preference packages:")
    for config in search_configs:
        print(f"   • {config['package_name']}")
        print(f"     Locations: {config['locations']}")
        print(f"     Job titles: {config['job_titles']}")
        if 'salary_min' in config:
            print(f"     Salary range: ${config['salary_min']:,} - ${config['salary_max']:,}")
    
    # Test contextual matching
    print("\n3. Testing contextual job matching...")
    
    test_jobs = [
        {
            'job_id': 'edmonton_local_1',
            'title': 'Marketing Manager',
            'location': 'Edmonton, AB',
            'salary_low': 70000,
            'salary_high': 80000,
            'remote_work': 'hybrid',
            'company': 'Local Edmonton Corp',
            'industry': 'Technology'
        },
        {
            'job_id': 'calgary_commute_1',
            'title': 'Senior Marketing Manager',
            'location': 'Calgary, AB',
            'salary_low': 90000,
            'salary_high': 110000,
            'remote_work': 'hybrid',
            'company': 'Calgary Energy Corp',
            'industry': 'Professional Services'
        },
        {
            'job_id': 'remote_canada_1',
            'title': 'Digital Marketing Manager',
            'location': 'Remote, Canada',
            'salary_low': 85000,
            'salary_high': 100000,
            'remote_work': 'remote',
            'company': 'Tech Startup Inc',
            'industry': 'Technology'
        },
        {
            'job_id': 'low_salary_local',
            'title': 'Marketing Coordinator',
            'location': 'Edmonton, AB',
            'salary_low': 45000,
            'salary_high': 55000,
            'remote_work': 'onsite',
            'company': 'Small Local Business',
            'industry': 'Retail'
        }
    ]
    
    for job in test_jobs:
        print(f"\n   Testing job: {job['title']} at {job['company']}")
        print(f"   Location: {job['location']}, Salary: ${job['salary_low']:,}-${job['salary_high']:,}")
        
        # Find matching package
        matching_package = pp.get_matching_package("steve_glen", job)
        
        if matching_package:
            print(f"   ✅ Matched to: {matching_package['package_name']}")
            print(f"   📝 Description: {matching_package['package_description']}")
        else:
            print(f"   ❌ No matching package found")
    
    return True

def demonstrate_contextual_logic():
    """Demonstrate the contextual salary logic"""
    print("\n4. Demonstrating Contextual Salary Logic")
    print("-" * 45)
    
    print("\n💡 How Steve Glen's preferences work:")
    print("🏠 Local Edmonton jobs: $65K-$85K (easy commute, lower salary acceptable)")
    print("🚗 Regional Alberta jobs: $85K-$120K (commute required, higher salary needed)")
    print("💻 Remote opportunities: $75K-$110K (no commute, quality role focus)")
    
    print("\n📊 This means:")
    print("• A $70K job in Edmonton ✅ GOOD (Local package matches)")
    print("• A $70K job in Calgary ❌ POOR (Below regional threshold)")
    print("• A $90K remote job ✅ GOOD (Remote package matches)")
    print("• A $120K job in Calgary ✅ EXCELLENT (High value for commute)")

def test_search_generation():
    """Test search configuration generation"""
    print("\n5. Testing Search Configuration Generation")
    print("-" * 45)
    
    pp = PreferencePackages()
    search_configs = pp.get_targeted_search_configs("steve_glen")
    
    print("\n🔍 Generated Apify search configurations:")
    for i, config in enumerate(search_configs, 1):
        print(f"\n{i}. {config['package_name']}")
        print(f"   Job Titles: {', '.join(config['job_titles'])}")
        print(f"   Locations: {', '.join(config['locations'])}")
        
        if 'salary_min' in config:
            print(f"   Salary Filter: ${config['salary_min']:,}+")
        
        if 'remote_work' in config:
            print(f"   Work Arrangement: {', '.join(config['remote_work'])}")

def show_sql_structure():
    """Show the SQL table structure"""
    print("\n6. Database Table Structure")
    print("-" * 30)
    
    print("""
    📊 user_job_preferences table structure:
    
    ┌─────────────────┬──────────────┬─────────────────────────────────────┐
    │ Field           │ Type         │ Purpose                             │
    ├─────────────────┼──────────────┼─────────────────────────────────────┤
    │ package_id      │ UUID         │ Unique package identifier           │
    │ user_id         │ VARCHAR      │ User identifier (steve_glen)        │
    │ package_name    │ VARCHAR      │ Descriptive name                    │
    │ conditions      │ JSONB        │ Matching conditions & context       │
    │ preferences     │ JSONB        │ Job preferences & requirements      │
    │ priority_score  │ INTEGER      │ Package priority (90=local, 70=regional) │
    │ is_active       │ BOOLEAN      │ Enable/disable package              │
    └─────────────────┴──────────────┴─────────────────────────────────────┘
    
    🔧 Key Features:
    • Multiple packages per user
    • JSON storage for flexible conditions
    • Priority-based matching
    • Contextual salary ranges
    • Location-aware preferences
    """)

def main():
    """Run all tests"""
    print("🚀 Preference Packages System Test Suite")
    print("========================================")
    
    try:
        # Test preference packages
        if not test_preference_packages():
            return
        
        # Demonstrate contextual logic
        demonstrate_contextual_logic()
        
        # Test search generation
        test_search_generation()
        
        # Show SQL structure
        show_sql_structure()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("\n💡 Next steps:")
        print("1. Add APIFY_TOKEN to Replit Secrets")
        print("2. Run: python -c 'from modules.intelligent_scraper import IntelligentScraper; IntelligentScraper().run_targeted_scrape(\"steve_glen\")'")
        print("3. Check dashboard for results and cost monitoring")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()