from fastapi import FastAPI, HTTPException, UploadFile, File, Request, Form
from pydantic import BaseModel
import pandas as pd
import math, csv, asyncio
import os, random, json, shutil, datetime, psutil
from PIL import Image
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import Optional, List
from mongodb import add_prod_to_collection, update_prod_by_id, update_image, delete_item, get_all_prod, get_item_by_id, find_account_by_username_and_password
import base64
import tempfile
from PIL import Image
import io
import requests
from requests.exceptions import SSLError
from BaseModel import CreateProductRequest, DeleteProductRequest, UpdateProductRequest, LoginUserRequest, CreateUserRequest, UpdateUserRequest, DeleteUserRequest

app = FastAPI()
# app.mount("/image", StaticFiles(directory="image"), name="image")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
################################
#path_img
img_path = './image/'
link_img_path = 'http://localhost:3000/Images/'
################################

html = f"""
<!DOCTYPE html>
<html>
    <head>
        <title>FastAPI on Vercel</title>
    </head>
    <body>
        <div class="bg-gray-200 p-4 rounded-lg shadow-lg">
            <h1>Hello from FastAPI</h1>
            <ul>
                <li><a href="/docs">/docs</a></li>
                <li><a href="/redoc">/redoc</a></li>
            </ul>
            <p>Powered by <a href="https://vercel.com" target="_blank">Vercel</a></p>
        </div>
    </body>
</html>
"""




# up img to imgbb
def upload_images(image_base64):
    url = "https://api.imgbb.com/1/upload"
    api_key = 'b99ea31917346513ac1e4047e79d7f5e'
    
    # with open(image, "rb") as file:
    payload = {
            "key": api_key,
            "image": image_base64,
    }
    response = requests.post(url, payload)
        
    # Xử lý phản hồi từ máy chủ
    # if response.status_code == 200:
    #         result = response.json()
    #         if result['status'] == 200:
    #             return result['data']['url']
    #         else:
    #             return result['error']['message']
    # else:
    #         return "Error when upload image!"
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 200:
            return result['data']['url']
            print(f"Image uploaded successfully. URL: {result['data']['url']}")
        else:
            return result['error']['message']
            print(f"Error: {result['error']['message']}")
    else:
        try:
            error_data = response.json()
            return error_data['error']['message']
        except:
            return f"Error: {response.status_code} - {response.text}"


# def upload_images(image_data):
#     url = "https://api.imgbb.com/1/upload"
#     api_key = 'b99ea31917346513ac1e4047e79d7f5e'
    
#     # Tạo một tệp tạm thời và ghi dữ liệu từ 'UploadFile' vào tệp này
#     # with tempfile.NamedTemporaryFile(delete=False) as temp:
#     #     temp.write(image_data.read())
#     #     temp_path = temp.name
    
#     # # Đọc dữ liệu ảnh từ tệp tạm thời
#     # image = Image.open(temp_path)
    
#     # Tiến hành xử lý ảnh tại đây (ví dụ: thay đổi kích thước, áp dụng bộ lọc, v.v.)
#     # ...
    
#     # Chuyển đổi ảnh thành dữ liệu base64
#     # buffered = io.BytesIO()
#     # image.save(buffered, format="JPEG")
#     # image_base64 = base64.b64encode(buffered.getvalue())

#     payload = {
#         "key": api_key,
#         "image": base64.b64encode(image_data.file.read()),
#     }
    
#     response = requests.post(url, payload)
    
#     # Xử lý phản hồi từ máy chủ
#     if response.status_code == 200:
#         result = response.json()
#         if result['status'] == 200:
#             image_url = result['data']['url']
#             # Xóa tệp tạm thời
#             # os.remove(temp_path)
#             return image_url
#         else:
#             error_message = result['error']['message']
#             # Xóa tệp tạm thời
#             # os.remove(temp_path)
#             return error_message
#     else:
#         # Xóa tệp tạm thời
#         # os.remove(temp_path)
#         return "Error"



def get_image_response(url: str, auth=None):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Referer": "https://www.google.com/",
        }
        response = requests.get(
            url,
            headers=headers,
            auth=auth,
            timeout=10,
            verify=False,
        )
        # self.log(response.text, 'response')
    except requests.exceptions.Timeout:
        
        return None
    except Exception:
        return None
    return response

# @app.get("/image")
# async def get_image_data(url: str):
#     """
#     API endpoint to fetch an image from a URL and return it.
    
#     Args:
#         url (str): The URL of the image to fetch.
    
#     Returns:
#         Response: The image content with the correct media type.
#     """
#     image_response = get_image_response(url)

#     # Return the image content with the correct media type
#     return image_response
@app.post("/image")
def get_image_data(request: ImageRequest):
    """
    Endpoint API lấy hình ảnh từ một URL trong request body (JSON) và trả về dưới dạng response.
    """
    # Lấy URL từ request body
    image_url = request.url
    
    image_response = get_image_response(image_url)
    return image_response



@app.get("/")
async def root():
    return HTMLResponse(html)

# Handle products
@app.get("/api/v1/product/show")
async def get_products():
    collect = 'product'
    # Mở file CSV và đọc dữ liệu
    data = get_all_prod(collect)
    return data


@app.post("/api/v1/product/update")
def update_products(product: UpdateProductRequest):
    id_product = product.id_product
    id_user_src = product.id_user_src
    word = product.word
    meaning = product.meaning
    note = product.note
    user_add = product.user_add
    subject = product.subject
    src_img = product.image
    list_id_img = product.list_id_img

    word = word if word != "" else None
    meaning = meaning if meaning != "" else None
    note = note if note != "" else None
    user_add = user_add if user_add != "" else None
    subject = subject if subject != "" else None
    list_id_img = list_id_img if list_id_img != "" else None

    # print(word, meaning, note, user_add, subject)
    if list_id_img is not None:
        if list_id_img == '':
            list_id_img = []
        list_id_img = list_id_img.split(",")
        list_id_img = list(map(int, list_id_img))
    else:
        list_id_img = []



    list_link_img = []
    if src_img is not None:
        for items in src_img:
            image_base64 = items['attachment']
            link = upload_images(image_base64)
            list_link_img.append(link)

    collect = 'product'
    data_img = update_image(id_product, list_id_img, list_link_img, collect)
    # print(data_img)
    product = {}
    if word is not None:
        product["word"] = word
    if meaning is not None:
        product["meaning"] = meaning
    if note is not None:
        product["note"] = note
    if user_add is not None:
        product["user_add"] = user_add
    if subject is not None:
        product["subject"] = subject

    product["image"] = data_img



    update_prod_by_id(id_product, product, collect)

    # Trả về phản hồi thành công
    return {"message": "Thay đổi thông tin từ thành công!"}


@app.delete("/api/v1/product/delete")
def delete_products(product: DeleteProductRequest):
    id_product = int(product.id_product)
    try:
        collection = 'product'
        result = delete_item(id_product, collection)
        return result
    except Exception as e:
        # Xử lý ngoại lệ (ví dụ: ghi log lỗi, trả về thông báo lỗi)
        return {"message": f"Đã xảy ra lỗi: {str(e)}"}
        # Trả về thông báo lỗi

@app.post("/api/v1/product/add")
async def create_products(product: CreateProductRequest):
    # print(product)
    word = product.word
    meaning = product.meaning
    note = product.note
    user_add = product.user_add
    subject = product.subject
    src_img = product.image
    print("hallo")

    date = datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')

    link_img ={}
    list_link_img = []
    if src_img is not None:
        i = 0
        for items in src_img:
            image_base64 = items['attachment']
            link = upload_images(image_base64)
            link_img = {'id': i,'link': link}
            list_link_img.append(link_img)
            i  = i + 1

    new_product = {
        "word": word,
        "meaning": meaning,
        "note": note,
        "image": list_link_img,
        "user_add": user_add,
        "date": date,
        "subject": subject
    }

    collect = 'product'
    add_prod_to_collection(new_product, collect)

    return {"message": f"Đã add thêm từ {word} vào từ điển!"}

# Handle Users
@app.get("/api/v1/user/show")
async def get_users():
    collect = 'account'
    # Mở file CSV và đọc dữ liệu
    data = get_all_prod(collect)
    return data

@app.post("/api/v1/user/add")
async def create_user(user: CreateUserRequest):
    id_user_add = user.id_user_add
    user_name = user.user_name
    password = user.password
    role = user.role
    src_img = user.image
    # print(id_user_add)
    # print(src_img)

    user = get_item_by_id(int(id_user_add), 'account')
    

    if user["role"] != "admin":
        return {"message": "Bạn khun có quyền tạo thêm user mới, chỉ người có vai trò Admin mới tạo được!"}
    
    date = datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')


    link_img = "https://raw.githubusercontent.com/longcule/react-dic/main/build/Y_png.jpg"
    # file_name = f"item_{random.randint(0, 100000)}"
    # path_to_image = f"{img_path}{file_name}.png"
    if src_img is not None:
        # with open(path_to_image, "wb") as image:
        #     image.write(src_img.file.read())
        image_base64 = src_img[0]['attachment']
        link_img = upload_images(image_base64)
        # if os.path.exists(path_to_image):
        #         os.remove(path_to_image)
        
    # Tạo đối tượng người dùng mới
    new_user = {
        "user_name": user_name,
        "password": password,
        "image": link_img,
        "role": role,
        "date": date
    }
    add_prod_to_collection(new_user, 'account')

    # return JSONResponse(content=new_user)
    return {"message": f"Đã add thêm user {user_name} với vai trò {role} !"}

@app.post("/api/v1/user/update")
def update_users(user: UpdateUserRequest):
        
        id_user_src = user.id_user_src
        id_user_target = user.id_user_target
        user_name = user.user_name
        old_password = user.old_password
        new_password = user.new_password
        image = user.image


        user_name = None if user_name == "" else user_name
        old_password = None if old_password == "" else old_password
        new_password = None if new_password == "" else new_password
        image = None if image == "" else image
        
        # Mở file json và đọc dữ liệu
        # with open("accounts.json", "r") as file:
        #     user = json.load(file)
        user = get_item_by_id(int(id_user_src), 'account')
        user_change = get_item_by_id(int(id_user_target), 'account')
        user_src_role = user['role']



        if user_src_role == "employee":
                if int(id_user_src) == int(id_user_target):
                    user_change_name = user_change["user_name"]
                    if user_name is not None:
                        user["user_name"] = user_name
                    if old_password is not None and new_password is not None:
                        if old_password == user["password"]:
                            user["password"] = new_password
                        else: 
                            return {"message":"Ôi bạn ơi, mật khẩu bạn nhập sai rồi, vui lòng nhập lại!"}
                    if old_password is not None or new_password is not None:
                        if old_password is None:
                            return {"message":"Vui lòng nhập mật khẩu cũ!"}
                        elif new_password is None:
                            return {"message":"Vui lòng nhập mật khẩu mới!"}

                    if image is not None:
                        link_img = upload_images(image)
                        user["image"] = link_img
                    user.pop('_id', None)
                    update_prod_by_id(id_user_src, user, 'account')
                    return {"message": f"Đã thay đổi thông tin user {user_change_name} thành công!"}

                elif int(id_user_src) != int(id_user_target):
                    return {"message": "Ôi bạn ơi, bạn không phải Admin nên không thay đổi được thông tin tài khoản của người khác nhé"}

        elif user_src_role == "admin":
                user_change_name = user_change["user_name"]
                if user_name is not None:
                    user_change["user_name"] = user_name
                if new_password is not None:
                    user_change["password"] = new_password

                if image is not None:
                    link_img = upload_images(image)
                    user_change["image"] = link_img
                user_change.pop('_id', None)
                update_prod_by_id(id_user_src, user_change, 'account')

                return {"message": f"Đã thay đổi thông tin user {user_change_name} thành công!"}
    
@app.delete("/api/v1/user/delete")
def delete_users(user: DeleteUserRequest):
    id_user_src = user.id_user_src
    id_user_target = user.id_user_target
    try:
            user = get_item_by_id(int(id_user_src), 'account')
            print("hi")
            # Mở file JSON và đọc dữ liệu
            role_user_src = user["role"]

        # Tìm hàng có id_product tương ứng và cập nhật giá trị
            if role_user_src == 'employee':
                print("hii")
                if int(id_user_src) == int(id_user_target):
                        data = delete_item(int(id_user_target), 'account')
                        return data
                else:
                        return {"message": f"Bạn không phải admin nên không thể xóa tài khoản này!"}
            
            elif role_user_src == "admin":
                print("hiii")
                data = delete_item(int(id_user_target), 'account')  
                return data   

    except Exception as e:
        # Xử lý ngoại lệ (ví dụ: ghi log lỗi, trả về thông báo lỗi)
        return {"message": f"Đã xảy ra lỗi khi xóa account: {str(e)}"}
        # Trả về thông báo lỗi

# Handle Login
@app.post("/api/v1/user/login")
async def login( user: LoginUserRequest):
    user_name = user.user_name
    password = user.password
    user = find_account_by_username_and_password('account', user_name, password)
    return user

# # Handle edit history
# @app.get("/api/v1/product/history/show/{id_product}")
# async def get_products_history(id_product: int):
#     product = []
#     try:
#         with open("products_update.json", "r") as file:
#             products = json.load(file)

#         for items in products:
#             if items["id"] == id_product:
#                 product.append(items)
#     except FileNotFoundError:
#         return {"message": "Không tìm thấy tệp dữ liệu."}

#     return JSONResponse(content=product)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)




