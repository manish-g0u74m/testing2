from app import create_app
# from pyngrok import ngrok
import os

# # Set your ngrok auth token here
# os.environ["NGROK_AUTHToken"] = "2w0BmAY93mORFWguKImQTEgz6h0_2cKXJ5dkgAmZjdkHyWGdA"  # Replace with your actual token

app = create_app()

# # Open a tunnel to port 5000
# public_url = ngrok.connect(5000).public_url
# print(f"\n===== Restaurant Recommendation System =====")
# print(f"Public URL: {public_url}")
# print(f"Share this link to access your application from anywhere!")
# print("===========================================\n")

#if __name__ == '__main__':
 #   app.run(host='0.0.0.0', port=5000)
#from app import create_app

#app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
