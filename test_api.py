import requests
import json

def test_api():
    print("Testing connection to NoComply BG3 Dialogue Finder API...")
    
    # Prepare search parameters
    data = {
        'search_term_1': 'tadpole',
        'search_by_1': 'dialogue',
        'search_term_2': 'Astarion',
        'search_by_2': 'character',
        'search_term_3': '',
        'search_by_3': 'type'
    }
    
    try:
        # Make API request
        response = requests.post(
            "https://nocomplydev.pythonanywhere.com/multi_search",
            headers={
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.8",
                "Connection": "keep-alive",
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "https://nocomplydev.pythonanywhere.com",
                "Referer": "https://nocomplydev.pythonanywhere.com/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
            },
            data=data
        )
        
        if response.status_code == 200:
            results = response.json()
            print(f"Connection successful! Found {len(results)} results.")
            
            if results:
                print("\nSample result:")
                sample = results[0]
                for key, value in sample.items():
                    print(f"{key}: {value}")
        else:
            print(f"API request failed with status code {response.status_code}")
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_api()
    print("\nPress Enter to exit...")
    input() 