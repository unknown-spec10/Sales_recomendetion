import json

def extract_all_products_final():
    """Final correct extraction of all products from JSON"""
    
    print("🔧 FINAL CORRECT EXTRACTION")
    print("=" * 50)
    
    try:
        with open('data.json', 'r') as f:
            content = f.read().strip()
        
        # The file contains multiple JSON objects separated by },\n{
        # Let's split by this pattern and rebuild proper JSON objects
        
        # First, let's wrap the entire content in an array to make it valid JSON
        # Replace },\n{ with },\n{ but wrap in array
        
        # Split by '},\n{' pattern
        json_parts = content.split('},\n{')
        
        print(f"📝 Found {len(json_parts)} JSON parts after splitting on '}},{{' pattern")
        
        # Fix the parts to be valid JSON objects
        json_objects = []
        for i, part in enumerate(json_parts):
            if i == 0:
                # First part already has opening brace
                json_objects.append(part + '}')
            elif i == len(json_parts) - 1:
                # Last part already has closing brace
                json_objects.append('{' + part)
            else:
                # Middle parts need both braces
                json_objects.append('{' + part + '}')
        
        print(f"📝 Created {len(json_objects)} complete JSON objects")
        
        all_products = []
        companies_found = {}
        
        for i, json_str in enumerate(json_objects):
            try:
                print(f"\n📦 Processing JSON Object {i+1}...")
                data_group = json.loads(json_str)
                
                if 'data' in data_group and 'docs' in data_group['data']:
                    docs = data_group['data']['docs']
                    print(f"     Found {len(docs)} products")
                    
                    # Show company breakdown for this JSON object
                    obj_companies = {}
                    for product in docs:
                        company = product.get('businessLine', {}).get('name', '')
                        if company:
                            obj_companies[company] = obj_companies.get(company, 0) + 1
                    
                    for company, count in obj_companies.items():
                        print(f"     {company}: {count} products")
                    
                    for product in docs:
                        company_name = product.get('businessLine', {}).get('name', '')
                        product_line = product.get('productLineName', '')
                        product_id = product.get('id', '')
                        
                        if company_name and product_line:
                            if company_name not in companies_found:
                                companies_found[company_name] = []
                            
                            companies_found[company_name].append({
                                'id': product_id,
                                'product_line': product_line
                            })
                            
                            all_products.append({
                                'id': product_id,
                                'company_name': company_name,
                                'product_line': product_line,
                                'tuple': (company_name, product_line)
                            })
                else:
                    print("     No 'data.docs' found in this object")
                
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing JSON object {i+1}: {e}")
                print(f"   Object starts with: {json_str[:100]}...")
                continue
        
        print("\n" + "=" * 50)
        print("📊 FINAL EXTRACTION RESULTS:")
        print(f"Total products extracted: {len(all_products)}")
        
        print("\n🏢 Companies found:")
        for company, products in companies_found.items():
            print(f"   {company}: {len(products)} products")
        
        # Generate tuples
        tuples_list = []
        for product in all_products:
            tuple_entry = (product['company_name'], product['product_line'])
            if tuple_entry not in tuples_list:
                tuples_list.append(tuple_entry)
        
        # Save corrected data - replace the existing files
        with open('products_with_tuples.json', 'w') as f:
            json.dump(all_products, f, indent=2)
        
        with open('business_line_tuples.json', 'w') as f:
            json.dump(tuples_list, f, indent=2)
        
        print(f"\n💾 Updated 'products_with_tuples.json' with {len(all_products)} products")
        print(f"💾 Updated 'business_line_tuples.json' with {len(tuples_list)} tuples")
        
        # Show sample from each company
        print(f"\n📋 SAMPLE DATA:")
        for company, products in companies_found.items():
            print(f"\n🏢 {company} ({len(products)} products):")
            for i, product in enumerate(products[:3]):
                print(f"   {i+1}. {product['product_line']} (ID: {product['id']})")
            if len(products) > 3:
                print(f"   ... and {len(products)-3} more")
        
        return all_products, tuples_list, companies_found
        
    except Exception as e:
        print(f"❌ Error extracting products: {e}")
        import traceback
        traceback.print_exc()
        return [], [], {}

if __name__ == "__main__":
    products, tuples, companies = extract_all_products_final()
    
    if len(products) == 44:
        print(f"\n🎉 SUCCESS! Extracted all {len(products)} products correctly!")
        print("🔄 The API will automatically reload with the new data.")
    elif len(products) > 20:
        print(f"\n✅ IMPROVED! Extracted {len(products)} products (was 20 before)")
        print("🔄 The API will automatically reload with the new data.")
    else:
        print(f"\n⚠️ Still only got {len(products)} products, expected 44")
