import requests

data = {
    "name": "李四",
    "gender": "男",
    "age": 20,
    "college": "计算机学院"
}

response = requests.post(
    "http://127.0.0.1:5000/student",
    json=data
)

print("状态码：", response.status_code)
print("返回内容：")
print(response.text)