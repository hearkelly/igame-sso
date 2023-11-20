import requests

# Define the API endpoint URL
api_url = "https://id.twitch.tv/oauth2/token?client_id=x80ohduafgkshvv7rnsf1r3c8nd5lz&client_secret=16mj47uav7xzrvlkue4say0jqqd16p&grant_type=client_credentials"

# Send the POST request
response = requests.post(api_url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    print("Request was successful")
    # You can access the response data as well
    response_data = response.json()
    print("Response data:", response_data)
else:
    print(f"Request failed with status code: {response.status_code}")
    print("Response content:", response.text)
