import requests
import traceback
import time
import os
import json

# API 密钥
CF_API_TOKEN    =  os.environ["CF_API_TOKEN"]
CF_ZONE_ID      =  os.environ["CF_ZONE_ID"]
CF_DNS_NAME     =  os.environ["CF_DNS_NAME"]

headers = {
    'Authorization': f'Bearer {CF_API_TOKEN}',
    'Content-Type': 'application/json'
}

def get_cf_speed_test_ip(timeout=10, max_retries=5):
    for attempt in range(max_retries):
        try:
            # 发送 GET 请求，设置超时
            response = requests.get('https://ip.164746.xyz/ipTop.html', timeout=timeout)
            # 检查响应状态码
            if response.status_code == 200:
                return response.text
        except Exception as e:
            traceback.print_exc()
            print(f"get_cf_speed_test_ip Request failed (attempt {attempt + 1}/{max_retries}): {e}")
    # 如果所有尝试都失败，返回 None 或者抛出异常，根据需要进行处理
    return None

def delete_and_push_dns_records(ips):
    url = f"https://api.cloudflare.com/client/v4/zones/{CF_ZONE_ID}/dns_records?name={CF_DNS_NAME}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if 'result' in data:
            for record in data['result']:
                record_id = record['id']
                delete_dns_record(record_id)
    except requests.RequestException:
        pass  # 忽略错误

    for ip in ips:
        try:
            data = {
                "type": "A",
                "name": "best",
                "content": ip,
                "ttl": 60,
                "proxied": False
            }
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                print(f"cf_dns_change success: ---- Time: " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + " ---- ip：" + str(ip))
            else:
                print(f"cf_dns_change ERROR: ---- Time: " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + " ---- MESSAGE: " + str(response.text))
        except requests.RequestException:
            pass  # 忽略错误

def delete_dns_record(record_id):
    url = f"https://api.cloudflare.com/client/v4/zones/{CF_ZONE_ID}/dns_records/{record_id}"

    try:
        response = requests.delete(url, headers=headers)
        if response.status_code == 200:
            print(f"Deleted record_id: {record_id}")
        else:
            raise Exception(f"Failed to delete DNS record with ID {record_id}: {response.text}")
    except requests.RequestException:
        pass  # 忽略错误

# 主函数
def main():
    # 获取最新优选IP
    ip_addresses_str = get_cf_speed_test_ip()
    ip_addresses = ip_addresses_str.split(',')
    delete_and_push_dns_records(ip_addresses[0])

if __name__ == '__main__':
    main()
