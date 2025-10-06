#!/usr/bin/env python3
"""
Pure Gemini API Test Script
===========================

This script tests Google Gemini API directly without any Replit Agent involvement.
It will show exactly what JSON structure comes from Gemini vs. what is added by our system.

Goal: Determine if 'implicit_requirements', 'cover_letter_insights', etc. 
      come from Gemini API or are added by our application layer.
"""

import os
import json
import sys
from datetime import datetime

def test_pure_gemini_api():
    """Test Gemini API directly with minimal processing"""
    
    print("🔬 PURE GEMINI API TEST")
    print("=" * 50)
    print("Testing Google Gemini API directly without Replit Agent processing")
    print("Goal: Isolate pure API response vs. application additions")
    print("")
    
    # Check for API key
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY environment variable not found")
        print("Please set your Gemini API key and run the script again")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    try:
        # Import google-genai directly
        import google.genai as genai
        print("✅ google-genai imported successfully")
        
        # Initialize client
        client = genai.Client(api_key=api_key)
        print("✅ Gemini client initialized")
        
        # Test job data
        test_job = {
            "title": "Marketing Communications Coordinator",
            "description": """We are seeking a dynamic Marketing Communications Coordinator to join our growing team. This role is perfect for someone passionate about marketing communications and content creation.

Key Responsibilities:
- Develop and execute marketing communication strategies across multiple channels
- Create compelling content for websites, social media, email campaigns, and print materials
- Coordinate marketing campaigns from concept to completion
- Manage social media accounts and engage with online communities
- Support event planning and execution for trade shows and corporate events
- Collaborate with cross-functional teams including sales, product, and design
- Monitor and analyze marketing performance metrics
- Maintain brand consistency across all communications
- Assist with public relations activities and media outreach

Required Qualifications:
- Bachelor's degree in Marketing, Communications, Journalism, or related field
- 2-3 years of experience in marketing communications or related role
- Excellent written and verbal communication skills
- Proficiency in marketing tools (HubSpot, Mailchimp, Hootsuite)
- Experience with Adobe Creative Suite (Photoshop, InDesign, Illustrator)
- Strong project management and organizational skills
- Knowledge of SEO principles and content marketing best practices
- Social media marketing experience across LinkedIn, Twitter, Facebook, Instagram
- Ability to work in fast-paced environment and manage multiple projects

Preferred Qualifications:
- Experience with marketing automation platforms
- Basic HTML/CSS knowledge
- Google Analytics certification
- Experience in B2B technology sector
- Bilingual capabilities (English/French)

What We Offer:
- Competitive salary: CAD 45,000 - 55,000
- Comprehensive benefits package including health, dental, and vision
- Professional development opportunities and training budget
- Flexible work arrangements (hybrid model)
- Dynamic startup environment with growth opportunities
- Modern office space in downtown Edmonton

Company: TechStart Edmonton
Location: Edmonton, AB (Hybrid)
Employment Type: Full-time""",
            "company": "TechStart Edmonton"
        }
        
        print(f"📝 Test Job: {test_job['title']}")
        print(f"📍 Company: {test_job['company']}")
        print(f"📄 Description: {len(test_job['description'])} characters")
        print("")
        
        # Create the exact prompt that would be sent to Gemini
        prompt = f"""Analyze this job posting and return a JSON response with the following structure:

Job Title: {test_job['title']}
Company: {test_job['company']}
Description: {test_job['description']}

Please provide a JSON response with this exact structure:
{{
  "primary_industry": "industry name",
  "secondary_industries": ["industry1", "industry2"],
  "seniority_level": "entry/mid/senior",
  "authenticity_score": 0.0-1.0,
  "skills_analysis": [
    {{
      "skill_name": "skill name",
      "importance_rating": 1-10,
      "reasoning": "explanation"
    }}
  ],
  "structured_data": {{
    "compensation": {{
      "salary_range": {{
        "min": number,
        "max": number,
        "currency": "currency"
      }},
      "benefits": ["benefit1", "benefit2"]
    }},
    "work_arrangement": {{
      "type": "remote/hybrid/onsite",
      "location": "location",
      "remote_flexibility": true/false
    }},
    "experience_requirements": {{
      "years_required": "X-Y",
      "education_level": "level",
      "preferred_fields": ["field1", "field2"]
    }},
    "ats_optimization": {{
      "keywords": [
        {{
          "keyword": "keyword",
          "importance_level": "high/medium/low",
          "category": "category"
        }}
      ]
    }}
  }}
}}

Return only valid JSON, no additional text or explanations."""

        print("🚀 Sending request to Gemini API...")
        print(f"📏 Prompt length: {len(prompt)} characters")
        print("")
        
        # Make API call with the latest model
        response = client.models.generate_content(
            model='gemini-2.0-flash-001',
            contents=prompt
        )
        
        print("✅ Response received from Gemini API")
        
        # Extract response text
        response_text = response.text if hasattr(response, 'text') and response.text else str(response)
        
        print(f"📏 Response length: {len(response_text)} characters")
        print("")
        
        # Try to parse as JSON
        try:
            # Clean response text (remove any markdown formatting)
            clean_text = response_text.strip()
            if clean_text.startswith('```json'):
                clean_text = clean_text[7:]
            if clean_text.endswith('```'):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()
            
            # Parse JSON
            gemini_json = json.loads(clean_text)
            
            print("✅ Successfully parsed JSON response")
            
            # Save pure Gemini response
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"tests/pure_gemini_api_response_{timestamp}.json"
            
            with open(output_file, 'w') as f:
                json.dump(gemini_json, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Pure Gemini JSON saved to: {output_file}")
            
            # Analyze the response structure
            print("")
            print("🔍 PURE GEMINI RESPONSE ANALYSIS:")
            print("-" * 40)
            
            print(f"🏷️  Top-level keys ({len(gemini_json)} total):")
            for key in gemini_json.keys():
                value = gemini_json[key]
                if isinstance(value, list):
                    print(f"   • {key}: array ({len(value)} items)")
                elif isinstance(value, dict):
                    print(f"   • {key}: object ({len(value)} keys)")
                else:
                    print(f"   • {key}: {type(value).__name__}")
            
            # Check for specific keys we're investigating
            investigated_keys = ['implicit_requirements', 'cover_letter_insights', 'red_flags']
            print("")
            print("🔎 INVESTIGATING SPECIFIC KEYS:")
            for key in investigated_keys:
                if key in gemini_json:
                    print(f"   ✅ '{key}' FOUND in pure Gemini response")
                else:
                    print(f"   ❌ '{key}' NOT FOUND in pure Gemini response")
            
            # Save readable summary
            summary_file = f"tests/pure_gemini_summary_{timestamp}.txt"
            with open(summary_file, 'w') as f:
                f.write("PURE GEMINI API RESPONSE ANALYSIS\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Test Date: {datetime.now()}\n")
                f.write(f"Model Used: gemini-2.0-flash-001\n")
                f.write(f"Job Tested: {test_job['title']}\n")
                f.write(f"Company: {test_job['company']}\n\n")
                
                f.write("RESPONSE STRUCTURE:\n")
                f.write("-" * 20 + "\n")
                for key in gemini_json.keys():
                    value = gemini_json[key]
                    if isinstance(value, list):
                        f.write(f"{key}: array ({len(value)} items)\n")
                    elif isinstance(value, dict):
                        f.write(f"{key}: object ({len(value)} keys)\n")
                    else:
                        f.write(f"{key}: {type(value).__name__}\n")
                
                f.write(f"\nKEY INVESTIGATION:\n")
                f.write("-" * 20 + "\n")
                for key in investigated_keys:
                    status = "FOUND" if key in gemini_json else "NOT FOUND"
                    f.write(f"{key}: {status}\n")
                
                f.write(f"\nRAW JSON RESPONSE:\n")
                f.write("-" * 20 + "\n")
                f.write(json.dumps(gemini_json, indent=2, ensure_ascii=False))
            
            print(f"📄 Analysis summary saved to: {summary_file}")
            
            print("")
            print("🎯 CONCLUSION:")
            print("-" * 20)
            print("The files above contain the pure Gemini API response without any")
            print("Replit Agent processing. Compare this with your system output to")
            print("determine what data comes from Gemini vs. your application layer.")
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON response: {e}")
            print("Raw response:")
            print(response_text)
            
            # Save raw response for debugging
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            raw_file = f"tests/gemini_raw_response_{timestamp}.txt"
            with open(raw_file, 'w') as f:
                f.write(f"Raw Gemini API Response\n")
                f.write(f"Timestamp: {datetime.now()}\n")
                f.write(f"Model: gemini-2.0-flash-001\n\n")
                f.write(response_text)
            
            print(f"💾 Raw response saved to: {raw_file}")
            return False
            
    except ImportError:
        print("❌ ERROR: google-genai not available")
        print("Please install: pip install google-genai")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting Pure Gemini API Test...")
    print("This will test Google Gemini API directly without Replit Agent involvement")
    print("")
    
    success = test_pure_gemini_api()
    
    if success:
        print("")
        print("✅ TEST COMPLETED SUCCESSFULLY")
        print("Check the generated files in tests/ folder for pure Gemini API output")
    else:
        print("")
        print("❌ TEST FAILED")
        print("Check error messages above for details")
    
    sys.exit(0 if success else 1)