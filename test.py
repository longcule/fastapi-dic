import requests
import base64

def upload_images(image_list):
    url = "https://api.imgbb.com/1/upload"
    api_key = 'b99ea31917346513ac1e4047e79d7f5e'
    
    for image_path in image_list:
        with open(image_path, "rb") as file:
            payload = {
                "key": api_key,
                "image": base64.b64encode(file.read()),
            }
            response = requests.post(url, payload)
            
            # Xử lý phản hồi từ máy chủ
            if response.status_code == 200:
                result = response.json()
                if result['status'] == 200:
                    print(f"Upload thành công: {result['data']['url']}")
                else:
                    print(f"Lỗi khi tải lên ảnh: {result['error']['message']}")
            else:
                print("Lỗi kết nối đến máy chủ tải lên ảnh.")

# Sử dụng hàm
image_list = ["images.png",]
upload_images(image_list)